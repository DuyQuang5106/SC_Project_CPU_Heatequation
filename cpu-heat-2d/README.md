# 2D CPU Heat Simulation Using Explicit Finite Difference Method

Project này mô phỏng phân bố nhiệt trên một chip CPU 2D bằng phương pháp sai phân hữu hạn explicit. Code chỉ dùng NumPy cho tính toán mảng và Matplotlib cho hình ảnh/animation. GIF được lưu bằng backend Pillow của Matplotlib.

## 1. Trực quan bài toán vật lý

CPU nóng lên vì khi transistor chuyển trạng thái, điện năng không biến mất mà một phần lớn biến thành nhiệt. Khi CPU chạy tải cao hơn, nhiều phép tính hơn được thực hiện, nên lượng nhiệt sinh ra trong vùng core lớn hơn.

Ta mô hình hóa chip như một tấm phẳng 2D vì trong project nhập môn này ta quan tâm phân bố nhiệt trên mặt chip, không đi sâu vào chiều dày. Nhiệt ở vùng core lan dần sang các vùng xung quanh. Biên ngoài chip được coi là đang tiếp xúc với hệ thống làm mát, nên nhiệt độ ở bốn cạnh được giữ cố định.

Các đại lượng chính:

- `u(x, y, t)`: nhiệt độ tại vị trí `(x, y)` và thời điểm `t`, đơn vị độ C.
- `alpha`: hệ số khuếch tán nhiệt. `alpha` càng lớn thì nhiệt lan càng nhanh.
- `Q(x, y)`: nguồn nhiệt. Trong project này `Q` khác 0 ở vùng CPU core và bằng 0 ở ngoài core.

## 2. Mô hình toán học

Phương trình nhiệt 2D có nguồn nhiệt:

```text
du/dt = alpha * (d2u/dx2 + d2u/dy2) + Q(x, y)
```

Ý nghĩa:

- `du/dt`: tốc độ thay đổi nhiệt độ theo thời gian.
- `d2u/dx2 + d2u/dy2`: toán tử Laplace 2D, đo độ cong của trường nhiệt độ. Nếu một điểm lạnh hơn xung quanh, nó có xu hướng nóng lên; nếu nóng hơn xung quanh, nó có xu hướng truyền nhiệt ra ngoài.
- `alpha`: điều khiển tốc độ lan nhiệt.
- `Q(x, y)`: lượng nhiệt sinh thêm mỗi giây tại từng vị trí.

Điều kiện ban đầu:

```text
u(x, y, 0) = 25
```

Ban đầu toàn bộ chip ở nhiệt độ phòng 25°C.

Điều kiện biên:

```text
u = 25 ở bốn cạnh chip
```

Nghĩa là mép ngoài chip được làm mát và luôn bị kéo về nhiệt độ cố định. Để so sánh `weak_cooling` và `strong_cooling` rõ hơn trong thời gian mô phỏng ngắn, code còn có thêm một hệ số làm mát đơn giản `cooling_rate`. Khi `cooling_rate = 0`, ta quay về đúng mô hình phương trình nhiệt có nguồn và biên cố định.

## 3. Rời rạc hóa

Ta chia chip thành lưới `N x N`. Mỗi ô lưới là một điểm tính nhiệt độ.

- `dx`: khoảng cách giữa hai điểm lưới theo trục x.
- `dy`: khoảng cách giữa hai điểm lưới theo trục y. Project dùng `dx = dy`.
- `dt`: bước thời gian.
- `U[i, j]`: nhiệt độ tại điểm lưới hàng `i`, cột `j`.
- `n`: chỉ số bước thời gian. `U` tại bước `n` biểu diễn nhiệt độ ở thời điểm `t = n * dt`.

Lưới càng mịn thì mô phỏng càng chi tiết, nhưng chạy chậm hơn và yêu cầu `dt` nhỏ hơn để ổn định.

## 4. Công thức explicit finite difference

Xấp xỉ đạo hàm thời gian:

```text
du/dt ≈ (U_new[i,j] - U[i,j]) / dt
```

Nó nói rằng tốc độ đổi nhiệt độ bằng nhiệt độ mới trừ nhiệt độ cũ, chia cho bước thời gian.

Xấp xỉ đạo hàm bậc hai theo x:

```text
d2u/dx2 ≈ (U[i+1,j] - 2U[i,j] + U[i-1,j]) / dx^2
```

Biểu thức này đo xem điểm hiện tại khác hai hàng xóm trái/phải nhiều hay ít.

Xấp xỉ đạo hàm bậc hai theo y:

```text
d2u/dy2 ≈ (U[i,j+1] - 2U[i,j] + U[i,j-1]) / dx^2
```

Vì `dx = dy`, mẫu số đều là `dx^2`.

Thay vào phương trình nhiệt:

```text
U_new[i,j] =
    U[i,j]
    + r * (U[i+1,j] + U[i-1,j] + U[i,j+1] + U[i,j-1] - 4U[i,j])
    + dt * Q[i,j]
```

Trong đó:

```text
r = alpha * dt / dx^2
```

Trực quan: nhiệt độ mới tại một điểm bằng nhiệt độ cũ, cộng phần trao đổi nhiệt với 4 hàng xóm, cộng nhiệt do CPU core sinh ra.

Trong code có thêm tùy chọn cooling:

```text
U_new = U_new - dt * cooling_rate * (U[i,j] - boundary_temperature)
```

Nếu `cooling_rate` lớn, chip mất nhiệt nhanh hơn về phía nhiệt độ làm mát. Nếu không muốn dùng phần mở rộng này, đặt `cooling_rate = 0`.

## 5. Điều kiện ổn định

Với phương pháp explicit cho phương trình nhiệt 2D:

```text
r <= 1/4
```

Nếu `r` quá lớn, nghiệm số có thể dao động vô lý hoặc nổ lên rất nhanh. Đây không phải CPU thật nóng lên, mà là lỗi do chọn bước thời gian quá lớn.

Cách chọn tham số:

1. Chọn `grid_size`.
2. Tính `dx = chip_size / (grid_size - 1)`.
3. Chọn `alpha`.
4. Chọn `dt` sao cho:

```text
dt <= dx^2 / (4 * alpha)
```

Trong code, nếu scenario không ổn định, chương trình sẽ báo lỗi và gợi ý `dt` tối đa.

## 6. Thiết kế project code

Cấu trúc thư mục:

```text
cpu-heat-2d/
├── main.py
├── solver.py
├── scenarios.py
├── visualization.py
├── outputs/
└── README.md
```

Vai trò từng file:

- `main.py`: chạy toàn bộ project, gọi solver và lưu hình.
- `solver.py`: chứa hàm `solve_heat_equation()`, công thức sai phân, kiểm tra ổn định.
- `scenarios.py`: chứa các bộ tham số mô phỏng.
- `visualization.py`: vẽ heatmap, animation GIF, đồ thị `Tmax(t)`.
- `outputs/`: nơi lưu ảnh PNG và GIF.

## 7. Code Python

Code đầy đủ nằm trong các file `.py` của project:

- `solver.py`: mô phỏng nhiệt bằng sai phân explicit.
- `scenarios.py`: định nghĩa `low_load`, `high_load`, `weak_cooling`, `strong_cooling`, `low_alpha`, `high_alpha`.
- `visualization.py`: lưu heatmap, animation và đồ thị.
- `main.py`: chạy tất cả scenario.

## 8. Giải thích code

`U` là ma trận nhiệt độ kích thước `grid_size x grid_size`. Mỗi phần tử `U[i, j]` là nhiệt độ tại một điểm trên chip.

`Q` là ma trận nguồn nhiệt cùng kích thước với `U`. Ở ngoài core, `Q = 0`. Trong vùng core, `Q = q_strength`, nghĩa là core liên tục sinh nhiệt.

Core được định nghĩa bằng `core_fraction`. Ví dụ `core_fraction = 0.25` nghĩa là core là một hình vuông ở giữa chip, có cạnh khoảng 25% kích thước lưới.

Vòng lặp thời gian trong `solve_heat_equation()` làm các việc sau:

1. Lưu `Tmax` hiện tại.
2. Lưu snapshot hoặc frame animation nếu đến thời điểm cần lưu.
3. Tính `U_new` từ `U` bằng công thức explicit.
4. Reset bốn cạnh về nhiệt độ biên.
5. Gán `U = U_new` để đi sang bước thời gian tiếp theo.

Phải reset boundary sau mỗi bước vì công thức update chỉ mô tả lan nhiệt bên trong chip. Điều kiện biên là ràng buộc vật lý: bốn cạnh luôn được làm mát ở nhiệt độ cố định.

`Tmax` được lưu bằng:

```python
tmax[step] = float(np.max(u))
```

Nó cho biết nhiệt độ nóng nhất trên chip tại từng thời điểm.

## 9. Cách chạy project

Vào thư mục project:

```bash
cd cpu-heat-2d
```

Cài thư viện:

```bash
pip install numpy matplotlib pillow
```

Chạy:

```bash
python main.py
```

Sau khi chạy, kiểm tra:

```text
outputs/
├── comparison_tmax.png
├── low_load/
├── high_load/
├── weak_cooling/
├── strong_cooling/
├── low_alpha/
└── high_alpha/
```

Mỗi thư mục scenario có:

- heatmap snapshot tại vài thời điểm.
- heatmap cuối.
- animation GIF.
- đồ thị `Tmax(t)`.

Muốn sửa tham số, mở `scenarios.py`:

- `alpha`: tăng để nhiệt lan nhanh hơn.
- `q_strength`: tăng để CPU core sinh nhiệt mạnh hơn.
- `grid_size`: tăng để lưới mịn hơn.
- `dt`: bước thời gian. Phải giữ điều kiện `r <= 1/4`.
- `total_time`: thời gian mô phỏng.
- `cooling_rate`: tăng để mô phỏng hệ thống làm mát mạnh hơn.

## 10. Phân tích kết quả

Heatmap cho thấy nhiệt bắt đầu tăng ở core, sau đó lan ra xung quanh. Màu sáng hơn nghĩa là nhiệt độ cao hơn.

Đồ thị `Tmax(t)` cho thấy điểm nóng nhất trên chip tăng theo thời gian như thế nào. Ban đầu thường tăng nhanh, sau đó chậm dần khi nhiệt sinh ra được cân bằng bởi quá trình truyền ra biên làm mát.

So sánh `low_load` và `high_load`: `high_load` có `q_strength` lớn hơn nên `Tmax` tăng nhanh hơn và đạt nhiệt độ cao hơn.

So sánh `low_alpha` và `high_alpha`: `high_alpha` làm nhiệt lan nhanh ra ngoài. Điều này có thể làm vùng core bớt tập trung nhiệt, nhưng cũng làm nhiều vùng khác nóng lên nhanh hơn.

So sánh `weak_cooling` và `strong_cooling`: cooling mạnh có `cooling_rate` lớn hơn, nên chip thoát nhiệt tốt hơn và `Tmax` thấp hơn.

Khi nghiệm tiến tới trạng thái ổn định, heatmap thay đổi rất ít theo thời gian và đường `Tmax(t)` gần như nằm ngang.

## 11. Gợi ý báo cáo khoảng 10 trang

Một cấu trúc hợp lý:

1. **Trang bìa và tóm tắt**: tên project, mục tiêu, phương pháp, kết quả chính.
2. **Giới thiệu bài toán**: vì sao CPU nóng lên, vì sao cần mô phỏng nhiệt.
3. **Mô hình vật lý**: chip 2D, core sinh nhiệt, biên làm mát.
4. **Mô hình toán học**: phương trình nhiệt 2D, điều kiện đầu, điều kiện biên.
5. **Phương pháp số**: lưới `N x N`, `dx`, `dt`, công thức explicit.
6. **Điều kiện ổn định**: trình bày `r <= 1/4` và cách chọn tham số.
7. **Thiết kế chương trình**: giải thích các file `main.py`, `solver.py`, `scenarios.py`, `visualization.py`.
8. **Kết quả mô phỏng**: đưa heatmap, GIF có thể thay bằng các frame, đồ thị `Tmax`.
9. **So sánh scenario**: low/high load, weak/strong cooling, low/high alpha.
10. **Kết luận và hướng phát triển**: nhận xét đạt được, hạn chế, ý tưởng mở rộng.

Hình nên đưa vào:

- Heatmap tại `t = 0`, giữa mô phỏng, cuối mô phỏng.
- Đồ thị `Tmax(t)` cho từng scenario.
- Hình `comparison_tmax.png`.

Công thức cần có:

- Phương trình nhiệt 2D có nguồn.
- Xấp xỉ đạo hàm thời gian.
- Xấp xỉ đạo hàm bậc hai theo x và y.
- Công thức update explicit.
- Điều kiện ổn định `r <= 1/4`.

Nhận xét nên viết:

- Core là vùng nóng nhất vì có nguồn nhiệt.
- Nhiệt lan từ vùng nóng sang vùng lạnh.
- Tải cao làm nhiệt độ tăng cao hơn.
- Làm mát mạnh làm giảm nhiệt độ toàn chip.
- `alpha` lớn làm nhiệt phân tán nhanh hơn.
- Sau đủ lâu, nghiệm có xu hướng tiến tới trạng thái gần ổn định.

## 12. Gợi ý slide thuyết trình 15 phút

Khoảng 10-12 slide:

1. **Title**: tên đề tài, tên sinh viên, môn học.
2. **Motivation**: CPU nóng lên vì đâu, tại sao cần mô phỏng.
3. **Physical Model**: chip 2D, core ở giữa, biên làm mát.
4. **Heat Equation**: trình bày phương trình và giải thích từng biến.
5. **Initial and Boundary Conditions**: ban đầu 25°C, bốn cạnh giữ lạnh.
6. **Grid Discretization**: lưới `N x N`, ý nghĩa `dx`, `dt`, `U[i,j]`.
7. **Explicit Formula**: công thức update và trực quan 4 hàng xóm.
8. **Stability**: điều kiện `r <= 1/4`, vì sao quan trọng.
9. **Code Structure**: sơ đồ các file trong project.
10. **Results**: heatmap và animation frame.
11. **Scenario Comparison**: đồ thị `comparison_tmax.png`.
12. **Conclusion**: kết luận, hạn chế, hướng phát triển.

Cách trình bày: nói đơn giản trước, công thức sau. Luôn gắn công thức với ý nghĩa vật lý: nguồn nhiệt làm core nóng lên, Laplace làm nhiệt lan ra, biên lạnh kéo nhiệt ra khỏi chip.

## Checklist hoàn thành project

- [ ] Có đủ cấu trúc `main.py`, `solver.py`, `scenarios.py`, `visualization.py`, `outputs/`, `README.md`.
- [ ] Chạy được `python main.py` không lỗi.
- [ ] Có heatmap snapshot trong từng thư mục scenario.
- [ ] Có animation GIF trong từng thư mục scenario.
- [ ] Có đồ thị `Tmax(t)` trong từng thư mục scenario.
- [ ] Có `outputs/comparison_tmax.png`.
- [ ] Hiểu được ma trận `U`, ma trận `Q`, vùng core và điều kiện biên.
- [ ] Biết kiểm tra điều kiện ổn định `r <= 1/4`.
- [ ] So sánh được load, cooling và alpha.
- [ ] Có đủ hình và công thức để viết báo cáo/thuyết trình.
