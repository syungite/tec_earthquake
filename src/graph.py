import numpy as np
import matplotlib.pyplot as plt

# 0.1から1の範囲でx2を生成
x1 = np.linspace(0, 1, 1000)
x2 = np.linspace(0.1, 1, 1000)

# グラフをプロット
plt.plot(x1, 700 * (x1 ** 0.3), label="true stress - true strain", color="red")
plt.plot(x2, 210 * (x2 ** (-0.7)), label="Work hardening rate", color="blue")

# x 軸の目盛の位置とラベルの設定
plt.xticks(
    ticks=[0.1 * i for i in range(11)],  # 0.0から1.0まで表示
    labels=[f"{0.1*i:.1f}" for i in range(11)]
)

plt.xlabel(r"$\varepsilon$")
plt.ylabel(r"$\sigma$")


plt.grid()
# 凡例と表示
plt.legend()
plt.show()


