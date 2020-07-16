import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']#设置字体以便支持中文
import numpy as np

def work1():
    x=np.arange(5)#柱状图在横坐标上的位置
    #列出你要显示的数据，数据的列表长度与x长度相同   
    y1 = [0.842024, 0.843156, 0.8468333, 0.65, 0.906]      # 静态成功率
    y2 = [0.84108, 0.84832, 0.8536, 0.51569, 0.719]      # 动态成功率
    y3 = [0.936646666667,0.937726666667,0.939586666667,0.57,0.939]

    bar_width=0.2#设置柱状图的宽度
    tick_label=['d=5', 'd=6', 'd=29', 'SilentWhisper', 'SpeedyMurmur']      # 横坐标刻度显示值
    #绘制并列柱状图
    plt.bar(x,y1,bar_width,color='none',linewidth=2,edgecolor='indianred',label='静态环境，L = 3', hatch="/")
    plt.bar(x+bar_width,y2,bar_width,color='none',linewidth=2,edgecolor='forestgreen',label='动态环境，L = 3', hatch="x")
    plt.bar(x+bar_width * 2,y3,bar_width,color='none',linewidth=2,edgecolor='midnightblue',label='动态环境，L = 1',hatch="\\")

    plt.legend(loc='upper right')#显示图例，即label
    #plt.xticks(x+bar_width/2,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.xticks(x+bar_width,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.ylim((0.5, 1))    #设置y轴范围
    plt.xlabel('多人通道网络与双人通道网络')
    plt.ylabel('成功率')
    #plt.title("成功率")
    plt.show()

def work2():
    x=np.arange(5)#柱状图在横坐标上的位置
    #列出你要显示的数据，数据的列表长度与x长度相同   
    y1 = [1.9322198, 1.9310076, 1.910405, 5.30, 1.87]      # 静态成功率
    y2 = [1.93399414402, 1.93069860313, 1.90997137294, 15.1289, 5.3518]      # 动态成功率
    y3 = [1.9339942,1.93094333333,1.90888333333,4.57,1.77]

    bar_width=0.2#设置柱状图的宽度
    tick_label=['d=5', 'd=6', 'd=29', 'SilentWhisper', 'SpeedyMurmur']      # 横坐标刻度显示值
    #绘制并列柱状图
    plt.bar(x,y1,bar_width,color='none',linewidth=2,edgecolor='indianred',label='静态环境，L = 3', hatch="/")
    plt.bar(x+bar_width,y2,bar_width,color='none',linewidth=2,edgecolor='forestgreen',label='动态环境，L = 3', hatch="x")
    plt.bar(x+bar_width * 2,y3,bar_width,color='none',linewidth=2,edgecolor='midnightblue',label='动态环境，L = 1',hatch="\\")

    plt.legend()#显示图例，即label
    #plt.xticks(x+bar_width/2,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.xticks(x+bar_width,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.ylim((0, 16))    #设置y轴范围
    plt.xlabel('多人通道网络与双人通道网络')
    plt.ylabel('路径长度（跳）')
    #plt.title("路径长度")
    plt.show()

def work3():
    x=np.arange(5)#柱状图在横坐标上的位置
    #列出你要显示的数据，数据的列表长度与x长度相同   
    y1 = [4.431534, 4.418874, 4.317363, 82.0, 18.3]      # 静态成功率
    y2 = [4.4969364155, 4.425480927, 4.32900384125, 64.2818, 16.055]      # 动态成功率
    y3 = [4.49088233333,4.45902666667,4.38806333333,10.54,5.46]

    bar_width=0.2#设置柱状图的宽度
    tick_label=['d=5', 'd=6', 'd=29', 'SilentWhisper', 'SpeedyMurmur']   # 横坐标刻度显示值
    #绘制并列柱状图
    plt.bar(x,y1,bar_width,color='none',linewidth=2,edgecolor='indianred',label='静态环境，L = 3', hatch="/")
    plt.bar(x+bar_width,y2,bar_width,color='none',linewidth=2,edgecolor='forestgreen',label='动态环境，L = 3', hatch="x")
    plt.bar(x+bar_width * 2,y3,bar_width,color='none',linewidth=2,edgecolor='midnightblue',label='动态环境，L = 1',hatch="\\")

    plt.legend()#显示图例，即label
    #plt.xticks(x+bar_width/2,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.xticks(x+bar_width,tick_label)#显示x坐标轴的标签,即tick_label,调整位置，使其落在两个直方图中间位置
    plt.ylim((0, 90))    #设置y轴范围
    plt.xlabel('多人通道网络与双人通道网络')
    plt.ylabel('路由开销（个）')
    #plt.title("路由开销")
    plt.show()


def main():
    work1()
    work2()
    work3()

main()
