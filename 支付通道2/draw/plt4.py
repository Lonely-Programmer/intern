import matplotlib.pyplot as plt
import matplotlib
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']

label_list = ['d=5, depth=4', 'd=6, depth=5', 'd=29, depth=3', 'SilentWhisper', 'SpeedyMurmur']    # 横坐标刻度显示值
num_list1 = [0.81118, 0.7830, 0.939, 0.65, 0.906]      # 静态成功率
num_list2 = [0.81118, 0.81118, 0.81118, 0.81118, 0.81118]      # 动态成功率
x = range(len(num_list1))
"""
绘制条形图
left:长条形中点横坐标
height:长条形高度
width:长条形宽度，默认值0.8
label:为后面设置legend准备
"""
rects1 = plt.bar(x, num_list1, width=0.4, alpha=0.8, color='green', label="静态实验")
rects2 = plt.bar(x, num_list2, width=0.4, color='blue', label="动态实验")
plt.ylim(0.8, 1)     # y轴取值范围
plt.ylabel("支付成功率")
"""
设置x轴刻度显示值
参数一：中点坐标
参数二：显示值
"""
plt.xticks([index + 0.2 for index in x], label_list)
plt.xlabel("网络路由方案")
plt.title("成功率")
plt.legend()     # 设置题注
# 编辑文本
for rect in rects1:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom")
for rect in rects2:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom")
plt.show()
