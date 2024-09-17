import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from vcd.reader import tokenize

# 配置 VCD 文件路径
vcd_file_path = 'network_data.vcd'

# 初始化图形
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 100)  # 根据需要调整
ax.set_ylim(-1, 2)   # 根据需要调整
ax.grid()

# 初始化数据
times = []
values = []

def init():
    line.set_data([], [])
    return line,

def update(frame):
    global times, values
    times.clear()
    values.clear()

    # 读取 VCD 文件中的数据
    with open(vcd_file_path, 'r') as f:
        for token in tokenize(f):
            if token[0] == 'date':
                # 处理日期信息（如果需要）
                continue
            if token[0] == 'end':
                break
            if token[0] == 'value':
                # 假设 token[1] 是时间，token[2] 是值
                times.append(token[1])
                values.append(token[2])
    
    line.set_data(times, values)
    ax.relim()
    ax.autoscale_view()
    return line,

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1000)
plt.show()
