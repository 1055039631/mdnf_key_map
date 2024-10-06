from pynput import keyboard
import subprocess
import time

proc = subprocess.Popen(['/bin/bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# 哪一个设备的事件，不同手机模拟器名称不一样
eventX = "event2"

# 触发sendevent的事件类型
EV_ABS = 3
EV_SYN = 0
EV_KEY = 1

# 触发sendevent的事件名称
# 用于索引每一个触摸事件。比如三个手指触摸，就三个slot
ABS_MT_SLOT = 47
# 每个触摸事件的id。比如三个手指触摸，就三个id
ABS_MT_TRACKING_ID = 57
# 触摸区域。这个好像没撒用
ABS_MT_TOUCH_MAJOR = 48

# 触摸区域。这个好像没撒用
ABS_MT_PRESSURE = 58
# x坐标
ABS_MT_POSITION_X = 53
# y坐标
ABS_MT_POSITION_Y = 54
# 同步信号
SYN_REPORT = 0
# 触摸
BTN_TOUCH = 330
# 手指
BTN_TOOL_FINGER = 325

# EV_KEY对应的两个值
# 按下
DOWN = 1
# 抬起
UP = 0

# event send EV_ABS:ABS_MT_POSITION_X:17192

# slot命令
commandSlot0 = b"event send EV_ABS:ABS_MT_SLOT:1\n"
commandSlot2 = b"event send EV_ABS:ABS_MT_SLOT:2\n"
commandSlot3 = b"event send EV_ABS:ABS_MT_SLOT:3\n"
commandSlot4 = b"event send EV_ABS:ABS_MT_SLOT:4\n"
# trackId命令
commandTrackId0 = b"event send EV_ABS:ABS_MT_TRACKING_ID:1\n"
commandTrackId2 = b"event send EV_ABS:ABS_MT_TRACKING_ID:2\n"
commandTrackId3 = b"event send EV_ABS:ABS_MT_TRACKING_ID:3\n"
commandTrackId4 = b"event send EV_ABS:ABS_MT_TRACKING_ID:4\n"
commandTrackIdF = b"event send EV_ABS:ABS_MT_TRACKING_ID:-1\n"

# 触摸区域命令
commandPressure4 = b"event send EV_ABS:ABS_MT_PRESSURE:1024\n"
# 触摸区域命令
commandPressure0 = b"event send EV_ABS:ABS_MT_PRESSURE:0\n"

# positionX命令
commandX_template = "event send EV_ABS:ABS_MT_POSITION_X:{}\n"
# positionY命令
commandY_template = "event send EV_ABS:ABS_MT_POSITION_Y:{}\n"
# syn命令
commandSyn0 = b"event send EV_SYN:0:0\n"
# 按键按下
commandDown = b"event send EV_KEY:BTN_TOUCH:1024\n"
# 按键抬起
commandUp = b"event send EV_KEY:BTN_TOUCH:UP\n"

# 是否发送send event开关，有时候不需要
send_event = True

# 键盘映射, 对应屏幕坐标位置
key_mapping = {
    '1': (21753, 25898),
    '2': (22049, 27253),

    'q': (3094, 25667),
    'w': (7986, 26339),
    'e': (11764, 28018),
    'r': (13311, 30723),

    'a': (4550, 29710),
    's': (6712, 23461),
    'd': (12355, 24522),
    'f': (16565, 27179),
    'g': (17088, 29730),

    'z': (21799, 28849),
    'x': (21799, 30562),
    'c': (17088, 29730),

    'Key.alt_r': (2412, 27673),
    'Key.space': (8525, 30771),
    'Key.ctrl': (31174, 766),

    # '1': (21799, 28849),
    # '2': (21799, 30562),
    # 'z': (21753, 25898),
    # 'x': (22049, 27253),
    # 'Key.up': (14234, 4253),
    # 'Key.down': (4391, 4295),
    # 'Key.left': (8555, 2121),
    # 'Key.right': (8988, 7965),

    'Key.up': (15234, 4253),
    'Key.down': (3391, 4295),
    'Key.left': (8555, 1121),
    'Key.right': (8988, 8965),
}

# 所有有触发行为的按键·
all_key = ['1', '2', 'q', 'w', 'e', 'r', 'a', 's', 'd', 'f', 'g', 'z', 'x', 'c', 'Key.alt_r', 'Key.space', 'Key.ctrl',
           'Key.up', 'Key.down', 'Key.left', 'Key.right']

# 方向键
drive_key = ['Key.left', 'Key.right', 'Key.up', 'Key.down', ]

# 支持长按的按键，用于平A
long_press_key = ['a']

# 双击按键 闪避要双击触发
double_key = ['Key.alt_r']

# 滑屏技能
slide_key = ['1', 'g', 'c']

# 滑屏技能对应的方向
slide_key_offset_map = {
    '1': (100, 0),
    'g': (0, 100),
    'c': (-100, 0),
}

# 当前按下了哪些按键
down_key = []

# 当前按下了哪些方向键
down_drive_key = []


# 获取方向键坐标，主要用于当按下两个方向键的时候，计算夹角方向
def get_drive_point():
    tx, ty = 0, 0
    for item in down_drive_key:
        x, y = key_mapping[item]
        tx = tx + x
        ty = ty + y
        # print(f"item = {item}  x = {x}  y={y} tx = {tx} ty ={ty}")
    tx = tx / len(down_drive_key)
    ty = ty / len(down_drive_key)
    # print(f"tx = {tx} ty ={ty}")
    return int(tx), int(ty)


# 按键按下
def key_down(slot, track_id, x, y):
    commands = [slot,
                track_id,
                commandX_template.format(x).encode(),
                commandY_template.format(y).encode(),
                commandPressure4,
                commandSyn0,
                ]
    proc.stdin.write(b"".join(commands))
    proc.stdin.flush()


# 按键抬起
def key_up(slot):
    commands = [slot,
                commandPressure0,
                commandTrackIdF,
                commandSyn0]
    proc.stdin.write(b"".join(commands))
    proc.stdin.flush()


# 滑动技能点击
def key_slide(slot, track_id, x, y, offset_x, offset_y):
    # 按下
    commands = [slot,
                track_id,
                commandX_template.format(x).encode(),
                commandY_template.format(y).encode(),
                commandPressure4,
                commandDown,
                commandSyn0,
                ]
    proc.stdin.write(b"".join(commands))
    proc.stdin.flush()
    move_x = x
    move_y = y
    # 根据offset连续滑动
    for i in range(62):
        move_y = move_y + offset_y
        move_x = move_x + offset_x
        if i == 61:
            time.sleep(0.0001)
        else:
            time.sleep(0.002)
        commands = [
            commandX_template.format(move_x).encode(),
            commandY_template.format(move_y).encode(),
            commandPressure4,
            commandSyn0, ]
        proc.stdin.write(b"".join(commands))
        proc.stdin.flush()
    # 滑到最后抬起
    commands = [
        commandUp,
        commandTrackIdF,
        commandSyn0]
    proc.stdin.write(b"".join(commands))
    proc.stdin.flush()


# 按键点击
def key_click(key, slot, track_id, x, y):
    commands = [slot,
                track_id,
                commandX_template.format(x).encode(),
                commandY_template.format(y).encode(),
                commandPressure4,
                commandSyn0,
                slot,
                commandPressure0,
                commandTrackIdF,
                commandSyn0]
    proc.stdin.write(b"".join(commands))
    proc.stdin.flush()
    # 双击再点一次
    if key in double_key:
        time.sleep(0.1)
        commands = [slot,
                    track_id,
                    commandX_template.format(x).encode(),
                    commandY_template.format(y).encode(),
                    commandPressure4,
                    commandSyn0,
                    slot,
                    commandPressure0,
                    commandTrackIdF,
                    commandSyn0]
        proc.stdin.write(b"".join(commands))
        proc.stdin.flush()


# 键盘按键按下
def press_key2(key):
    down_key.append(key)
    if key in drive_key:
        down_drive_key.append(key)
        x, y = get_drive_point()
        key_down(commandSlot0, commandTrackId0, x, y)
    elif key in long_press_key:
        x, y = key_mapping[key]
        key_down(commandSlot3, commandTrackId3, x, y)
    elif key in slide_key:
        x, y = key_mapping[key]
        offset_x, offset_y = slide_key_offset_map[key]
        key_slide(commandSlot2, commandTrackId2, x, y, offset_x, offset_y)
    else:
        x, y = key_mapping[key]
        key_click(key, commandSlot2, commandTrackId2, x, y)


# 键盘按键抬起
def release_key2(key):
    down_key.remove(key)
    if key in drive_key:
        down_drive_key.remove(key)
        if len(down_drive_key) == 0:
            key_up(commandSlot0)
        else:
            x, y = get_drive_point()
            key_down(commandSlot0, commandTrackId0, x, y)
    elif key in long_press_key:
        key_up(commandSlot3)


# 获取当前按下的按键
def get_key_str(key):
    return str(key).replace("'", "")


# 键盘按下
def on_keyboard_press(key):
    key_str = get_key_str(key)
    # if key_str in key_mapping:
    #     print(f"键 '{key_str}' 对应的值为：{key_mapping[key_str]}")
    # else:
    #     print(f"键 '{key_str}' 不在字典中")
    global send_event
    if key_str == '`':
        send_event = not send_event
    print(f"cur send_event is {send_event}")
    if key_str in all_key and send_event:
        if key_str not in down_key:
            print("this key is " + key_str)
            press_key2(key_str)


# 手指从按键抬起
def on_keyboard_release(key):
    key_str = get_key_str(key)
    # if key_str in key_mapping:
    #     print(f"键 '{key_str}' 对应的值为：{key_mapping[key_str]}")
    # else:
    #     print(f"键 '{key_str}' 不在字典中")
    if key_str == 'Key.esc':
        proc.stdin.write(b"quit\n")
        proc.stdin.flush()
        proc.stdin.close()
        return False

    if key_str in all_key and send_event:
        if key_str in down_key:
            print("release key is " + key_str)
            release_key2(key_str)


if __name__ == "__main__":
    proc.stdin.write(b"telnet localhost 5554\n")
    proc.stdin.flush()
    # todo 每个模拟器的auth不一样
    proc.stdin.write(b"auth 1U0IBTa4TnaWfecq\n")
    proc.stdin.flush()

    # Collect events until released
    with keyboard.Listener(
            on_press=on_keyboard_press,
            on_release=on_keyboard_release) as listener:
        listener.join()
