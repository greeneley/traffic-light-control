import matplotlib.pyplot as plt
import pandas as pd
import os
os.chdir(os.path.dirname(__file__))
current_dir = os.getcwd()
result_dir = current_dir + "/result"

def visualize(input_file=[]):

    csv_origin_file =  pd.read_csv(input_file[0], sep=";")
    csv_improve_file =  pd.read_csv(input_file[1], sep=";")

    X_step = csv_origin_file["step_time"]
    Y_speed = csv_origin_file["step_meanSpeed"] / 0.27
    Z_waiting = csv_origin_file["step_waiting"]

    x3_step = csv_improve_file["step_time"]
    y3_speed = csv_improve_file["step_meanSpeed"] / 0.27
    z3_waiting = csv_improve_file["step_waiting"]

    labels = ["origin", "improved", "turnoff", "3"]
    colors = ["blue", "green", "purple", "orange"]
    means = [Y_speed.mean(), y3_speed.mean()]
    queues = [Z_waiting.mean(), z3_waiting.mean()]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(X_step, Y_speed, color="blue", linewidth=1, label="origin")
    ax.plot(x3_step, y3_speed, color="orange", linewidth=1, label="improved")
    ax.set_xlabel("step")
    ax.set_ylabel("speed km/s")
    ax.set_title("Toc do phuong tien")
    ax.legend()
    fig.savefig(f"{result_dir}/speed.png", format='png', dpi=1200)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(X_step, Z_waiting, color="blue", linewidth=1, label="origin")
    ax.plot(x3_step, z3_waiting, color="orange", linewidth=1, label="improved")
    ax.set_xlabel("step")
    ax.set_ylabel("vehicles")
    ax.set_title("So luong phuong tien dang doi")
    ax.legend()
    fig.savefig(f"{result_dir}/queues.png", format='png', dpi=1200)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar("origine", Y_speed.mean(), color="blue")
    ax.bar("improved", y3_speed.mean(), color="orange")
    ax.set_ylabel("vehicles")
    ax.set_title("Toc do trung binh")
    ax.legend()
    for index, data in enumerate(means):
        ax.text(x=index, y=data + 1, s=f"{data:.2f}", fontdict=dict(fontsize=10), ha="center")
    fig.savefig(f"{result_dir}/speed_mean.png", format='png', dpi=1200)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar("origine", Z_waiting.mean(), color="blue")
    ax.bar("improved", z3_waiting.mean(), color="orange")
    ax.set_ylabel("vehicles")
    ax.set_title("Queue")
    ax.legend()
    for index, data in enumerate(queues):
        ax.text(x=index, y=data + 1, s=f"{data:.2f}", fontdict=dict(fontsize=10), ha="center")
    fig.savefig(f"{result_dir}/queues_mean.png", format='png', dpi=1200)