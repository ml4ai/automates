"""
Mask R-CNN
Train on the equation detection dataset.
------------------------------------------------------------
Usage: import the module (see Jupyter notebooks for examples), or run from
       the command line as such:

    # Train a new model starting from ImageNet weights
    python3 equation.py train --dataset=/path/to/dataset --subset=train --weights=imagenet

    # Train a new model starting from specific weights file
    python3 equation.py train --dataset=/path/to/dataset --subset=train --weights=/path/to/weights.h5
    
    # Resume training a model that you had trained earlier
    python3 equation.py train --dataset=/path/to/dataset --subset=train --weights=last
"""

import os
import sys
import time
import colorsys
import pandas as pd
import skimage.draw
import numpy as np

# Root directory of the project
ROOT_DIR = os.path.abspath("Mask_RCNN")

# Import Mask RCNN
sys.path.append(ROOT_DIR) # To find local version of the library

from mrcnn.config import Config
from mrcnn import utils
from mrcnn import model as modellib

# Path to trained weights file
COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")



############################################################
#  Configurations
############################################################

class EquationConfig(Config):
    """Configuration for training on the equations dataset.
    Derives from the base Config and overrides some values.
    """

    # Give the configuration a recognizable name
    NAME = "equation"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # Background + equation

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 100

    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.9

    # Backbone network architecture
    # Supported values are: resnet50, resnet101
    BACKBONE = "resnet50"

class EquationInferenceConfig(EquationConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1



############################################################
#  Dataset
############################################################

class EquationDataset(utils.Dataset):

    def load_equation(self, dataset_dir, subset):
        """Load a subset of the equation dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """
        # Add classes. We have only one class to add.
        self.add_class("equation", 1, "equation")

        # Train or validation dataset?
        # assert subset in ["train", "val"]
        csv_path = os.path.join(dataset_dir, "{}.csv".format(subset))
        dataset_dir = os.path.join(dataset_dir, subset)

        # Load csv annotations with pandas
        annotations = pd.read_csv(csv_path)

        for filename in annotations['filename'].unique():
            image_path = os.path.join(dataset_dir, filename)

            # get rows from dataframe for specific image
            img_annotations = annotations[annotations['filename'] == filename]

            # we get page dimensions
            # (should be the same in all rows for this image)
            width  = img_annotations['width'].iloc[0]
            height = img_annotations['height'].iloc[0]

            # collect bounding boxes
            bounding_boxes = []
            for i, row in img_annotations.iterrows():
                upper_left  = (row['ymin'], row['xmin'])
                lower_right = (row['ymax'], row['xmax'])
                aabb = dict(upper_left=upper_left, lower_right=lower_right)
                bounding_boxes.append(aabb)

            # add image data to dataset
            self.add_image(
                "equation",
                image_id=filename,  # use file name as a unique image id
                path=image_path,
                width=width,
                height=height,
                bounding_boxes=bounding_boxes)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
        Returns:
         masks: A bool array of shape [height, width, instance count] with
             one mask per instance.
         class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a equation dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        if image_info["source"] != "equation":
            return super(self.__class__, self).load_mask(image_id)

        # Convert bounding box to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["bounding_boxes"])], dtype=np.uint8)
        for i, aabb in enumerate(info["bounding_boxes"]):
            # Get indexes of pixels inside the bounding box and set them to 1
            rr, cc = skimage.draw.rectangle(start=aabb['upper_left'], end=aabb['lower_right'])
            mask[rr, cc, i] = 1

        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        return mask.astype(np.bool), np.ones([mask.shape[-1]], dtype=np.int32)

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "equation":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)



############################################################
#  Training
############################################################

def train(model, dataset_dir):
    """Train the model."""
    # Training dataset.
    dataset_train = EquationDataset()
    dataset_train.load_equation(dataset_dir, "train")
    dataset_train.prepare()

    # Validation dataset
    dataset_val = EquationDataset()
    dataset_val.load_equation(dataset_dir, "val")
    dataset_val.prepare()

    # TODO Image augmentation
    # http://imgaug.readthedocs.io/en/latest/source/augmenters.html
    # augmentation = iaa.SomeOf((0, 2), [
    #     iaa.Fliplr(0.5),
    #     iaa.Flipud(0.5),
    #     iaa.OneOf([iaa.Affine(rotate=90),
    #                iaa.Affine(rotate=180),
    #                iaa.Affine(rotate=270)]),
    #     iaa.Multiply((0.8, 1.5)),
    #     iaa.GaussianBlur(sigma=(0.0, 5.0))
    # ])

    # If starting from imagenet, train heads only for a bit
    # since they have random weights
    print("Train network heads")
    start = time.time()
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=20,
                # augmentation=augmentation,
                layers='heads')
    end = time.time()
    print("Trained network heads in {} seconds".format(end-start))

    print("Train all layers")
    start = time.time()
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=40,
                # augmentation=augmentation,
                layers='all')
    end = time.time()
    print("Trained all layers in {} seconds".format(end-start))



############################################################
#  Detection
############################################################

def detect(model, image_path):
    """Run detection on images in the given directory."""
    # Run model detection
    print("Running on {}".format(image_path))
    # Read image
    image = skimage.io.imread(args.image)
    # Detect objects
    r = model.detect([image], verbose=1)[0]
    # Draw bounding boxes
    draw_boxes(image, r['rois'])
    # Save output
    file_name = "equation_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    skimage.io.imsave(file_name, image)
    print("Saved to ", file_name)

def draw_boxes(image, boxes):
    """
    image: the image.
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    """
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
    else:
        assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

    # Generate random colors
    colors = random_colors(N)

    for i in range(N):
        num_instance, (y1, x1, y2, x2, class_id) = boxes[i]
        box = (y1, x1, y2, x2)
        color = colors[i]
        draw_box(image, box, color)

def draw_box(image, box, color):
    """Draw 3-pixel width bounding boxes on the given image array.
    color: list of 3 int values for RGB.
    """
    y1, x1, y2, x2 = box
    image[y1:y1 + 2, x1:x2] = color
    image[y2:y2 + 2, x1:x2] = color
    image[y1:y2, x1:x1 + 2] = color
    image[y1:y2, x2:x2 + 2] = color
    return image

def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors



############################################################
#  Command Line
############################################################

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Mask R-CNN for equation detection')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'detect'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/dataset/",
                        help='Root directory of the dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco' or 'imagenet'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--subset', required=False,
                        metavar="Dataset sub-directory",
                        help="Subset of dataset to run prediction on")
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "detect":
        assert args.subset, "Provide --subset to run prediction on"

    print("Weights:", args.weights)
    print("Dataset:", args.dataset)
    if args.subset:
        print("Subset:", args.subset)
    print("Logs:", args.logs)

    # Configurations
    if args.command == "train":
        config = EquationConfig()
    else:
        config = EquationInferenceConfig()
    config.display()

    # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config, model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config, model_dir=args.logs)
    
    # Select weights file to load
    if args.weights.lower() == "coco":
        weights_path = COCO_WEIGHTS_PATH
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)
    elif args.weights.lower() == "last":
        # Find last trained weights
        weights_path = model.find_last()
    elif args.weights.lower() == "imagenet":
        # Start from ImageNet trained weights
        weights_path = model.get_imagenet_weights()
    else:
        weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # Train or evaluate
    if args.command == "train":
        train(model, args.dataset)
    elif args.command == "detect":
        detect(model, args.image_path)
    else:
        print("'{}' is not recognized. Use 'train' or 'detect'".format(args.command))
