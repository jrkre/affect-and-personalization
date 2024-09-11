from __future__ import annotations
import logging
from collections import defaultdict
from pathlib import Path
import time
from typing import Union, List, Tuple, Dict, TypedDict, Optional
from types import NoneType
import yaml
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.widgets import Button
from detect_face_features import get_features_coordinates, get_frame_time,main 
import numpy as np
from Joint import Joint, JointTree



class Motion:
    def __init__(self):
        self.frames = 0
        self.frame_time = .03333
        self.animation = []
    
    def add_frame(self, frame_data):
        self.frames = self.frames + 1
        self.animation.append(frame_data)
    
    def joint_to_tf(self, joint):
        pass

    



class CharacterConfig():

    class JointDict(TypedDict):
        loc: List[int]
        name: str
        parent: Union[None, str]

    def __init__(self, char_cfg_fn: str) -> None:  # noqa: C901
        character_cfg_p = Path("./yaml/char_cfg.yaml")
        with open(str(character_cfg_p), 'r') as f:
            char_cfg = yaml.load(f, Loader=yaml.FullLoader)

        # validate image height
        try:
            self.img_height: int = char_cfg['height']
            assert isinstance(self.img_height, int), 'type not int'
            assert self.img_height > 0, 'must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in character height config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # validate image width
        try:
            self.img_width: int = char_cfg['width']
            assert isinstance(self.img_width, int), 'type not int'
            assert self.img_width > 0, 'must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in character width config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # based on height and width, determine what final img dimension will be (post padding)
        self.img_dim: int = max(self.img_height, self.img_width)

        # validate skeleton
        try:
            self.skeleton: List[CharacterConfig.JointDict] = []
            for joint in char_cfg['skeleton']:

                # ensure loc input is valid...
                loc: List[int] = joint['loc']
                assert len(loc) == 2, 'joint loc must be of length 2'
                assert loc[0] >= 0, 'x val must be >= 0'
                assert loc[0] < self.img_width, 'x val must be < image width'
                assert loc[1] >= 0, 'y val must be >= 0'
                assert loc[1] < self.img_height, 'y val must be < image height'

                # ... then scale to between 0-1 based on img dim
                loc_x: int = loc[0] #/ self.img_dim  # width
                loc_y: int = loc[1] #/ self.img_dim + (1 - self.img_height / self.img_dim)  # height

                # validate joint name
                name: str = joint['name']
                assert isinstance(name, str), 'name must be str'

                # validate joint parent
                parent: Union[None, str] = joint['parent']
                assert isinstance(parent, (NoneType, str)), 'parent must be str or NoneType'

                self.skeleton.append({'loc': [loc_x, loc_y], 'name': name, 'parent': parent})
        except AssertionError as e:
            msg = f'Error in character skeleton: {e}'
            logging.critical(msg)
            assert False, msg

        # validate skeleton joint parents
        try:
            names: List[str] = [joint['name'] for joint in self.skeleton]
            for joint in self.skeleton:
                assert isinstance(joint['parent'], NoneType) or joint['parent'] in names, f'joint.parent not None and not valid joint name: {joint}'
        except AssertionError as e:
            msg = f'Error in character skeleton: {e}'
            logging.critical(msg)
            assert False, msg

        # validate mask and texture files
        try:
            self.mask_p: Path = character_cfg_p.parent / 'mask.png'
            self.txtr_p: Path = character_cfg_p.parent / 'texture.png'
            assert self.mask_p.exists(), f'cannot find character mask: {self.mask_p}'
            assert self.txtr_p.exists(), f'cannot find character texture: {self.txtr_p}'
        except AssertionError as e:
            msg = f'Error validating character files: {e}'
            logging.critical(msg)
            assert False, msg

def convert_2d_points_to_3d(points_2d, z_coordinate):
    """Convert 2D coordinates to 3D coordinates.

    Parameters
    ----------
    points_2d
        Array like containing two dimensional (x, y) coordinates.
    z_coordinate
        Z coordinate to add to the 2D coordinates.

    Returns
    -------
    npt.ArrayLike
        An array of points containing the 2D points in points_2d
        with z_coordinate added to make the coordinates three
        dimensional.
    """
    points_3d = np.empty(
        (len(points_2d), 3), dtype=np.float64
    )
    points_3d[:, :2] = points_2d
    points_3d[:, 2] = z_coordinate
    return points_3d

def get_channels(joint_name):
    channels = ["z-pos", "x-pos", "y-pos", "z-rot", "x-rot", "y-rot"]
    range = None
    if joint_name == "root":
        range = 6
    else:
        return channels[3:]
    return channels[:range]
        
    

def config_to_joints(config):
    array = config.skeleton
    length = len(array)
    root_joint = Joint("root","root",(2001, 1400,0), get_channels("root"))

    tree = JointTree()
    tree.create_joint_from_joint(root_joint)
    count = 0

    last_node = "root"
    #print (array)
    while tree.__len__() != length:
        #print (joints.count())
        
        #print(count)
        
    
        names = tree.get_names_of_subtree(0)
        print(names)
        
        for x in names:
            print (x)
            for node in array:
                #print(f'comparing {x[0].name} and {node["name"]} count {count}')
                if(node["name"] == "root"):
                    print("only once")
                    array.remove(node)
                
                # print(x.__getitem__(names[count]).name)
                if node["parent"] == x:
                    print(f'found match {node['name']}')
                    pt = convert_2d_points_to_3d((node['loc'][0],node['loc'][1]),0)
                    new_node = Joint(offset=(node['loc'][0],node['loc'][1]), name=node['name'], identifier=node["name"],channels=get_channels(node['name']))
                    print(f'found match adding {node['name']} to {x}')
                    tree.create_joint_from_joint(node=new_node, parent_id=node["parent"])
                    
                    print(f'input: {x}')
                    last_node = tree.__getitem__(new_node.name)
                    
                    last_node=new_node.name
                    # print(joints.count())
                    # print(joints.get_names(list=[]))
                    array.remove(node)
                    # joints.print()
                    # print(len(array))
                    count = count + 1
        #tree.show(0)
    return root_joint


def joints_to_file(file, joints):

    data = joints.make_yaml()
    file = './output/output.yaml'
    with open(file, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

        
def coordinates_to_joint_offset(current_coordinates):
    count = 0

    # dots 49-68, only 40 to 60 represent the outer perimeter of the mouth
    mouth = []

    # dots 37-42, probably only using 38,39,41,42
    left_eye = []

    for x in current_coordinates:
        if count in range(49,68):
            mouth.append(x)
        elif count in range(37,42):
            left_eye.append(x)

        

    

def zero_joints():
    pass




if __name__ == "__main__":
    #main()
    #take in character config, parse it to joints, and record an animation
    config = CharacterConfig("")
    joints = config_to_joints(config)
    joints_to_file(joints)


    #main()
    print("here")
