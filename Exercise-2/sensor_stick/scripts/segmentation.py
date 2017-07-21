#!/usr/bin/env python

# Import modules
from pcl_helper import *

# TODO: Define functions as required

# Callback function for your Point Cloud Subscriber
def pcl_callback(pcl_msg):

    # TODO: Convert ROS msg to PCL data

    pcl_cloud=ros_to_pcl(pcl_msg)

    # TODO: Voxel Grid Downsampling

    vox=pcl_cloud.make_voxel_grid_filter()
    leafSize = 0.01
    vox.set_leaf_size(leafSize, leafSize, leafSize)
    cloud_vox=vox.filter()

    # TODO: PassThrough Filter

    passthrough=cloud_vox.make_passthrough_filter()
    filter_axis='z'
    passthrough.set_filter_field_name (filter_axis)
    axis_min = 0.6
    axis_max = 1.1
    passthrough.set_filter_limits (axis_min, axis_max)
    cloud_passthrough = passthrough.filter()

    # TODO: RANSAC Plane Segmentation

    segmented = cloud_passthrough.make_segmenter()
    segmented.set_model_type(pcl.SACMODEL_PLANE)
    segmented.set_method_type(pcl.SAC_RANSAC)
    threshold = 0.01
    segmented.set_distance_threshold(threshold)
    inliers,coefficients = segmented.segment()

    # TODO: Extract inliers and outliers

    cloud_table = cloud_passthrough.extract(inliers, negative = False)
    cloud_objects = cloud_passthrough.extract(inliers, negative = True)

    # TODO: Euclidean Clustering

    white_cloud = XYZRGB_to_RGB(cloud_objects)
    tree = white_cloud.make_kdtree()

    # 	Create a cluster extraction object
    ec = white_cloud.make_EuclideanClusterExtraction()

    # 	Set tolerances for distance threshold 
    # 	as well as minimum and maximum cluster size (in points)
    ec.set_ClusterTolerance(1)
    ec.set_MinClusterSize(10)
    ec.set_MaxClusterSize(250)

    # 	Search the k-d tree for clusters
    ec.set_SearchMethod(tree)

    # 	Extract indices for each of the discovered clusters
    cluster_indices = ec.Extract()

    # TODO: Create Cluster-Mask Point Cloud to visualize each cluster separately

    # TODO: Convert PCL data to ROS messages

    ros_cloud_table = pcl_to_ros(cloud_table)
    ros_cloud_objects = pcl_to_ros(cloud_objects)

    # TODO: Publish ROS messages
    pcl_objects_pub.publish(ros_cloud_objects)
    pcl_table_pub.publish(ros_cloud_table)


if __name__ == '__main__':

    # TODO: ROS node initialization
    rospy.init_node('clustering', anonymous=True)
   
    # TODO: Create Subscribers
    pcl_sub = rospy.Subscriber("/sensor_stick/point_cloud", pc2.PointCloud2, pcl_callback, queue_size=1)

    # TODO: Create Publishers
    pcl_objects_pub = rospy.Publisher("/pcl_objects", PointCloud2, queue_size=1)
    pcl_table_pub = rospy.Publisher("/pcl_table", PointCloud2, queue_size=1)

    # Initialize color_list
    get_color_list.color_list = []

    # TODO: Spin while node is not shutdown
    while not rospy.is_shutdown():
	rospy.spin()
