# /usr/bin/env python3
"""
Load a model ('simple_2d.h5')
Create local attributions using SHAP
Output a CSV file of explanations for train & test
Output contour plots of local attributions


"""

import os
import pathlib
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from synthetic_data.utils import resolve_output_path

output_path = resolve_output_path(pathlib.Path(__file__).parent.absolute())

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # or any {'0', '1', '2'}
np.random.seed(111)
np.set_printoptions(
    precision=3, suppress=True, linewidth=160, formatter={"float": "{: 0.3f}".format}
)

plt.close("all")


def my_tricontour(ax, x1, x2, y, z, labels=None, title=None):
    tri2 = ax.tricontourf(x1, x2, z)
    scatter = ax.scatter(x1, x2, c=y, label=y, marker=".")
    leg1 = ax.legend(*scatter.legend_elements(), loc="lower right", title="class")
    ax.set_title(title)
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    cbar2 = fig.colorbar(tri2, ax=ax, fraction=0.046, pad=0.04)
    cbar2.formatter.set_powerlimits((0, 0))
    cbar2.update_ticks()
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    # ax.set_aspect("equal", "box")
    ax.set_aspect("equal")

    return


SMALL = 14
MEDIUM = 16
LARGE = 18

plt.rc("font", size=SMALL)  # controls default text sizes
plt.rc("axes", titlesize=MEDIUM)  # fontsize of the axes title
plt.rc("axes", labelsize=MEDIUM)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SMALL)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SMALL)  # fontsize of the tick labels
plt.rc("legend", fontsize=SMALL)  # legend fontsize
plt.rc("figure", titlesize=LARGE)  # fontsize of the figure title

# load the data
with open("x.pkl", "rb") as f:
    X = pickle.load(f)

with open("y_label.pkl", "rb") as f:
    y = pickle.load(f)

x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# baseline = np.array([0.0, 0.0]).reshape(1,2)
# nsamples = 25

# TODO - get a grid of fixed points in [x1, x2] - so it's common across r values
# background = x_train[np.random.choice(x_train.shape[0], nsamples, replace=False)]

# x1_tmp = np.arange(-1, 1, 0.1)
# x2_tmp = np.arange(-1, 1, 0.1)
# m_grid = np.meshgrid(x1_tmp, x2_tmp, indexing="xy")
# background = np.vstack([m_grid[0].ravel(), m_grid[1].ravel()]).T

model = load_model("simple_2d.h5", compile=False)

# explain
# exp = shap.DeepExplainer(model, background)
exp = shap.DeepExplainer(model, x_train)
local_attr_list = exp.shap_values(x_train)
local_attr = np.array(local_attr_list).squeeze()

features = ["x1", "x2"]
attr_df = pd.DataFrame(data=np.array(local_attr), columns=features)
attr_df.to_csv(f"attr_round1.csv", index=False)

# comparison of input vs attributions
#
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
scatter = ax[0].scatter(x_train[:, 0], x_train[:, 1], c=y_train, label=y_train)
leg1 = ax[0].legend(*scatter.legend_elements(), loc="lower right", title="class")
ax[0].set_xlabel("x1")
ax[0].set_ylabel("x2")
ax[0].grid()

scatter2 = ax[1].scatter(local_attr[:, 0], local_attr[:, 1], c=y_train, label=y_train)
# ax[1].plot(background, "k+")
leg2 = ax[1].legend(*scatter2.legend_elements(), loc="lower right", title="class")
ax[1].set_xlabel("x1 attr")
ax[1].set_ylabel("x2 attr")
ax[1].grid()
plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
plt.savefig(f"{output_path}/scatter_round1.png", bbox_inches="tight")


# check contour levels for attr for x1 and x2
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
x1 = x_train[:, 0]
x2 = x_train[:, 1]
z = local_attr[:, 0]
my_tricontour(ax[0], x1, x2, y_train, z, labels=["x1", "x2"], title="x1 SHAP values")

z = local_attr[:, 1]
my_tricontour(ax[1], x1, x2, y_train, z, labels=["x1", ""], title="x2 SHAP values")

plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
plt.savefig(f"{output_path}/trif_round1.png", bbox_inches="tight")

# check contor levels for correlation
# fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
# tri1 = ax[0].tricontourf(x_train[:, 0], x_train[:, 1], local_attr[:, 0])
# scatter = ax[0].scatter(
#    x_train[:, 0], x_train[:, 1], c=y_train, label=y_train, marker="."
# )
##ax[0].plot(background[:, 0], background[:, 1], "w+")
# leg1 = ax[0].legend(*scatter.legend_elements(), loc="lower right", title="class")
# cbar1 = fig.colorbar(tri1, ax=ax[0])
# ax[0].set_title("x1 attributions")
# ax[0].set_xlabel("x1")
# ax[0].set_ylabel("x2")
## cbar1.set_label('x1 attribution')
# cbar1.formatter.set_powerlimits((0, 0))
# cbar1.update_ticks()

# tri2 = ax[1].tricontourf(x_train[:, 0], x_train[:, 1], local_attr[:, 1])
# scatter = ax[1].scatter(
#    x_train[:, 0], x_train[:, 1], c=y_train, label=y_train, marker="."
# )
# leg1 = ax[1].legend(*scatter.legend_elements(), loc="lower right", title="class")
# ax[1].set_title("x2 attribution")
# ax[1].set_xlabel("x1")
# ax[1].set_ylabel("x2")
# cbar2 = fig.colorbar(tri2, ax=ax[1])
# cbar2.formatter.set_powerlimits((0, 0))
# cbar2.update_ticks()
#
# plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
# plt.savefig(f"trif_round1.png", bbox_inches="tight")
plt.show()
