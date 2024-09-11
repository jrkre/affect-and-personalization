from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.widgets import Button
import argparse

import yaml

ix, iy = None, None
ax = None
implot = None
facial_features = []
cid = None

#feature name, node count for representation
features = [
    
    ["root", 1, ["root"]],
    ["nose", 
                3, 
                    ["base_nose", 
                     "left_nose", 
                     "right_nose"]],
            ["left_eye",
                8, 
                    ["inner_corner", 
                     "lower_right_middle", 
                     "lower_middle", 
                     "lower_left_middle",
                     "outer_corner",
                     "upper_left_middle",
                     "upper_middle",
                     "upper_right_middle"]], 
            ["left_eyebrow", 
                4,
                    ["inner",
                     "middle_right",
                     "middle_left",
                     "outer"]], 
            ["right_eye",
                8,
                    ["inner_corner", 
                     "lower_left_middle", 
                     "lower_middle", 
                     "lower_right_middle",
                     "outer_corner",
                     "upper_right_middle",
                     "upper_middle",
                     "upper_left_middle"]], 
            ['right_eyebrow', 
                4,
                    ["inner",
                     "middle_left",
                     "middle_right",
                     "outer"]] , 
            ["mouth", 
                12,
                    ["upper_center",
                     "upper_right_middle",
                     "upper_right",
                     "right_middle",
                     "lower_right",
                     "lower_right_middle",
                     "lower_center",
                     "lower_left_middle",
                     "lower_left",
                     "left_middle",
                     "upper_left",
                     "upper_left_middle"]]]

count = 0


def open_image(file):
    global height, width
    img = mpimg.imread(file)
    height, width = img.shape[0], img.shape[1]
    
    return img

def next(event):
    #create a new facial feature as a child of the current
    global count, facial_features
    count = count + 1

    global facial_features
    if len(facial_features) <= count:
        facial_features.append(FacialFeature(features[count], parent=features[count-1][0]))
    print(f'current feature: {features[count]}')
    global cid
    implot.figure.canvas.mpl_disconnect(cid)
    cid = implot.figure.canvas.mpl_connect('button_press_event', facial_features[count].add_node)


def prev(event):
    #go back to the parent of the current facial feature
    global count, facial_features
    if count == 0:
        return
    else:
        count = count - 1
    
    print(f'current feature: {features[count]}')

    global cid
    implot.figure.canvas.mpl_disconnect(cid)
    cid = implot.figure.canvas.mpl_connect('button_press_event', facial_features[count].add_node)


class Node:
    def __init__(self, coords, node_name, parent=None):
        self.coords = coords
        self.name = node_name
        self.parent = parent
    



class FacialFeature:
    '''
    FacialFeature represents a single facial feature as a tree of (x,y) nodes. 
    Connect FacialFeatures together to form a tf-tree kind of rig that can be used to animate it.
    The tree should kind of go like:

                base of nose
                /    |     \
            left eye |  right eye
            /      mouth        \
         eyebrow              eyebrow

    the goal is to export to yaml and have consistent files
    '''

    def __init__(self, feature, parent=None) -> None:
        self.parent = parent
        self.root = False


        if parent == None:
            self.root = True
        self.feature = feature[0]
        self.nodes_for_feature = feature[1]
        self.node_names = feature[2]

        
        self.node_count = 0
        self.nodes = []

    
    def add_node(self, event):
        #capture mouse click
        ix, iy = int(event.xdata), int(event.ydata)

        if (ix < 1 or iy < 1):
            #dont count button presses
            return

        #print(f'x = {ix}, y = {iy}')
        global count
        
        
        
        if count == 0:
            node_name = self.node_names[self.node_count]
            print(node_name)
        #append selected coord to list
        #print(self.node_names)
        if self.node_count == 0 and count == 0:
            
            self.nodes.append(Node((ix,iy), node_name=f'{self.node_names[self.node_count]}'))
        elif self.node_count == 0:
            self.nodes.append(Node((ix,iy), node_name=f'{self.feature}_{self.node_names[self.node_count]}',parent=facial_features[count-1].nodes[0].name))
        elif self.node_count >= self.nodes_for_feature:
            return
        elif self.node_count < self.nodes_for_feature:
            self.nodes.append(Node((ix,iy), node_name=f'{self.feature}_{self.node_names[self.node_count]}', parent=f'{self.feature}_{self.node_names[self.node_count-1]}'))
        
        self.node_count = self.node_count + 1
        
        global ax
        if ax != None:
            ax.plot(ix,iy,marker='v', color='red')

        self.print_next()
    
        
    def print_next(self):
        if self.node_count < self.nodes_for_feature:
            if self.node_count < self.nodes_for_feature:
                print(f'place the {self.node_names[self.node_count]} on {self.feature}')
            print(f'nodes left: {self.nodes_for_feature - self.node_count}')
        else:
            print("out of nodes~")
            return
        


    def plot_coords(self):
        global ax
        x_vals = [x[0] for x in self.coords]
        y_vals = [x[1] for x in self.coords]

        ax.plot(x_vals,y_vals, linewidth=1)
    

height = None
width = None

def facial_features_to_yaml(event):
    global height, width


    face = dict()
    node_list = []
    for a in facial_features:
        for b in a.nodes:
            current_node = dict(
                name= str(b.name),
                parent = str(b.parent),
                loc = b.coords
            )
            node_list.append(current_node)

    face['skeleton'] = node_list
    face['height'] =height
    face['width'] = width
    
    file = './output/output.yaml'
    with open(file, 'w') as outfile:
        yaml.dump(face, outfile, default_flow_style=False)



if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-f", "--file", required=True, help="file to be made into a character")
    args = vars(ap.parse_args())
    #print(args)
    img = open_image(args['file'])
    fig, ax = plt.subplots()
    
    
    axnext = plt.axes([0.9, 0.0, 0.1, 0.075])
    axprev = plt.axes([0.8, 0.0, 0.1, 0.075])
    bnext = Button(axnext, "next")
    bnext.on_clicked(next)
    bprev = Button(axprev, "prev")
    bprev.on_clicked(prev)

    axexp = plt.axes([0.5, 0.0, 0.1, 0.075])
    bnexp = Button(axexp, "export")
    bnexp.on_clicked(facial_features_to_yaml)


    facial_features.append(FacialFeature(feature=features[0]))
    #print(f'current feature: {features[count]}')

    implot = ax.imshow(img)
    
    facial_features[count].print_next()

    cid = implot.figure.canvas.mpl_connect('button_press_event', facial_features[count].add_node)


    #print(fig)
    
    plt.show()