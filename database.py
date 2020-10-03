class LabelStore:
    def __init__(self, root):
        self._version = 0
        self._label_structure = {
            root: None
        }
        self._label_snapshots = {
            self._version: self._label_structure.copy()
        }
    
    def add_label(self, label):
        if label[1] not in self._label_structure.keys():
            raise ValueError("Failed to add new label. Parent of node {} is not existed yet".format(label[0]))
        self._label_structure[label[0]] = label[1]

    def bump_version(self):
        self._version += 1
        self._label_snapshots[self._version] = self._label_structure.copy()
    
    def get_version(self):
        return self._version
    
    def get_labels(self):
        return self._label_structure.keys()
    
    def get_label_snapshot(self, version):
        return self._label_snapshots[version]
    
    def get_current_label_structure(self):
        return self._label_structure

class ImageStore:
    def __init__(self):
        self._images = {}
    
    def add_image(self, image, labels, label_version):
        if type(labels) is not list:
            raise TypeError("Image labels are not a list")

        self._images[image] = {
            "labels": labels,
            "label_version": label_version
        }
    
    def get_image_status(self, label_store):
        status = {}
        def get_label_children(label, label_structure):
                children = []
                for label_child, label_parent in label_structure.items():
                    if label_parent == label:
                        children.append(label_child)
                return set(children)

        for image, label_info in self._images.items():
            current_label_structure = label_store.get_current_label_structure()
            image_label_structure = label_store.get_label_snapshot(label_info["label_version"])
            labels = label_store.get_labels()
            
            image_status = "valid"
            # Check if label is matched
            for label in label_info["labels"]:
                if label not in labels:
                    image_status = "invalid"
                    break
            
            if image_status == "valid":
                # Check if label has new child node
                for label in label_info["labels"]:
                    snapshot_label_children = get_label_children(label, image_label_structure)
                    current_label_children = get_label_children(label, current_label_structure)
                    if snapshot_label_children != current_label_children:
                        image_status = "granularity_staged"
                
                # Check if parent label has new child node, if yes, overwrite image status
                for label in label_info["labels"]:
                    snapshot_label_children = get_label_children(image_label_structure[label], image_label_structure)
                    current_label_children = get_label_children(image_label_structure[label], current_label_structure)
                    if snapshot_label_children != current_label_children:
                        image_status = "coverage_staged"

            status[image] = image_status
        return status

class Database(object):

    def __init__(self, root):
        if type(root) is not str:
            raise TypeError("Root node should be a string")
        self._label_store = LabelStore(root)
        self._image_store = ImageStore()

    def add_nodes(self, nodes):
        if type(nodes) is not list:
            raise TypeError("Nodes is not a list")
        for node in nodes:
            if type(node) is not tuple and len(node) != 2:
                raise TypeError("Node is not a tuple of 2 elements")
            self._label_store.add_label(node)
        
        # Bump version of label store and make a snapshot
        self._label_store.bump_version()

        
    def add_extract(self, extract):
        if type(extract) is not dict:
            raise TypeError("Extract is not a list")

        label_version = self._label_store.get_version()
        for image, labels in extract.items():            
            self._image_store.add_image(image, labels, label_version)

    def get_extract_status(self):
        return self._image_store.get_image_status(self._label_store)