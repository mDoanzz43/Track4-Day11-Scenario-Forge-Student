MSSV: 202602839

# Lab 11 - Scenario Forge - Bao cao

Thi tran cua toi (`meta.json: _run.town`): **D**. Tat ca ket qua duoi day duoc tao bang ngan sach day du, `quick = false` (`meta.json: steps`).

## 1. Phat lai log co trung thuc khong? (buoc A)

Trong 400 kich ban, khong log nao bi loai do nguoi lai gay va cham (`replay.json: dropped_human_crash_logs = 0`). Planner tren log phat lai co 103 va cham, gom 95 `rear` va 8 `side`; the gioi phan ung chi co 1 va cham `side`, va khong co va cham nao xuat hien o ca hai che do (`replay.json: replay`, `reactive`, `crash_in_both = 0`).

Phan lon va cham replay la `rear` vi planner phanh som hon nguoi lai trong log, nhung xe bam duoi van chay theo quy dao da ghi va khong biet planner vua phanh. Day la va cham gia cua counterfactual replay. Vi du `replay.json: replay_only[0]` (scenario 0) bi dam sau trong replay, trong khi the gioi phan ung co `min_ttc_reactive = 10 s`: xe sau co the phanh va khong va cham.

## 2. Kich ban bat kha thi (buoc B)

`is_feasible` loai mau neu: (1) gia toc ngang cuc dai cua chuyen lan cosine `((pi/cutDur)^2 * 3.5/2)` vuot `mu*g`; (2) `cutBrake > mu*g`; (3) `pedV > 2.5 m/s`; (4) `cutV` khong nam trong `(0, 22] m/s`. Hai luat dau la gioi han bam duong/ma sat, luat ba ngan nguoi di bo thanh nguoi chay, luat bon ngan xe dung hoac toc do phi thuc te trong scene.

Cuoc san `cut_in` sinh nhieu mau bat kha thi nhat, bang `rear_ended`: moi cuoc 10 mau (`hunt.json: cut_in.infeasible`, `rear_ended.infeasible`); `bus_bypass` co 4 va `crosswalk_block` co 6. CEM bi hut ve cac mau nay vi chuyen lan nhanh, phanh gat hoac hanh vi cuc doan cho diem nguy hiem cao. Neu dem chung la va cham, ta se uoc luong qua cao rui ro cua nhung tinh huong khong the xay ra ngoai doi.

## 3. Monte Carlo cho biet gi? (buoc C1)

`mc.json`: `k = 2`, `n = 3000`, `p_hat = 6.6667e-4`, Wilson 95% `[1.8284e-4, 2.4277e-3]`; ca hai la `bus_bypass`. De sai so xap xi +/-20% cua p can `n ~= 96/p`, tuc khoang **144,000** lan chay.

`cut_in`, `crosswalk_block`, `rear_ended` va `other` chua xuat hien. Khong duoc bao xac suat 0; moi mode co can tren Wilson `1.2789e-3` (`mc.json: per_mode.<mode>.hi`).

## 4. Importance sampling, ESS va do suy bien (buoc C3)

| Seed | Mode | p | Hits | ESS | top_share |
|---:|---|---:|---:|---:|---:|
| 0 | bus_bypass | 1.9858e-4 | 40 | 131.70 | 0.270 |
| 0 | cut_in | zero-hit, upper 0.025 | 0 | 124.81 | 0 |
| 0 | crosswalk_block | 1.7469e-6 | 33 | 126.21 | 0.919 |
| 0 | rear_ended | zero-hit, upper 0.025 | 0 | 127.64 | 0 |
| 1 | bus_bypass | 3.4812e-4 | 34 | 122.50 | 0.472 |
| 1 | cut_in | zero-hit, upper 0.025 | 0 | 131.15 | 0 |
| 1 | crosswalk_block | 1.5600e-7 | 36 | 111.17 | 0.236 |
| 1 | rear_ended | zero-hit, upper 0.025 | 0 | 113.20 | 0 |
| 2 | bus_bypass | 2.4795e-4 | 33 | 130.67 | 0.295 |
| 2 | cut_in | zero-hit, upper 0.025 | 0 | 120.55 | 0 |
| 2 | crosswalk_block | 1.2759e-7 | 41 | 121.80 | 0.150 |
| 2 | rear_ended | zero-hit, upper 0.025 | 0 | 119.19 | 0 |

Nguon: `estimate.json: seeds[*].per`. Tong ba seed lan luot la `2.0033e-4`, `3.4828e-4`, `2.4807e-4`. `bus_bypass` dong y cung bac do lon voi Monte Carlo nhung thap hon point estimate MC; `crosswalk_block` seed 0 cao hon hai seed con lai khoang 11 lan. `top_share = 0.919` tai seed 0 cho thay gan toan bo uoc luong mode nay den tu mot mau nang, nen CI chuan chi la xap xi.

Ngan sach IS la 16,800 rollout (`estimate.json: budget`), nho hon khoang 144,000 MC can de dat sai so tuong doi 20% tai p MC. `other` lay truc tiep tu MC (`estimate.json: other.source = mc.json`) vi khong co ham nguy hiem co nghia de san mot tap gom moi va cham chua duoc gan nhan.

## 5. Cac kieu that bai (buoc C2 + 3D)

- `bus_bypass`: C2 chen qua xe buyt dung, di cham o `x < 112 m`; ego tiep can va dam C2. Cuoc san tim 136 mau (`hunt.json: bus_bypass.found`). Anh can nop: `evidence/shots/bus_bypass.png`.
- `crosswalk_block`: nguoi di bo P1 xuat hien sau xe buyt; ego phanh nhung than xe dung tren vach va chan duong P1. Cuoc san tim 13 mau (`hunt.json: crosswalk_block.found`). Anh can nop: `evidence/shots/crosswalk_block.png`.
- Cuoc san `cut_in` khong tim dung mode, chi tim 5 `bus_bypass`; cuoc san `rear_ended` chi tim 5 `crosswalk_block` (`hunt.json: *.found`). Do do chua co bang chung failure cho hai mode muc tieu nay, khong phai bang chung xac suat bang 0.

Neu chi dung mot cuoc san chung, CEM se co ve mode de tang score nhat va lap lai no. Ket qua tren cho thay ngay ca khi san rieng, objective `cut_in` va `rear_ended` van co the roi vao mode khac; san rieng tung mode la dieu kien can de tang do phu failure.

## 6. Sua planner (buoc E + 3D)

Policy duoc chon tren TRAIN la `{"cutinLat": 3.0}`. TRAIN: `fail = 2.1392e-6`, `fail_hi_seen = 5.6366e-6`, progress `216.20 m`, harsh braking `6.92` frame/run (`fix.json: chosen`). Baseline TRAIN co `fail = 5.4627e-4`, `fail_hi = 1.0439e-3`, progress `216.33 m`, harsh `7.54` (`fix.json: baseline_train`).

Tren TEST doc lap, policy moi co `fail = 7.1929e-8`, `fail_hi_seen = 1.3647e-7`, nhung `fail_hi = 3.8779e-2` do `bus_bypass` la unseen; progress `216.65 m`, harsh `7.50`. Baseline TEST co `fail = 1.2942e-4`, `fail_hi_seen = 2.2698e-4`, `fail_hi = 1.5059e-3`, progress `216.75 m`, harsh `7.76` (`fix.json: chosen_test`, `baseline_test`). Vi zero-hit phai cong can `3/(0.2*n)`, can hop le cua ban sua co the lon hon baseline du point estimate tot hon.

Tang `T` len 2.0 nghe co ve an toan hon vi tang khoang cach theo sau, nhung TRAIN van co `fail = 4.6845e-4`, kem xa `cutinLat = 2.6` (`3.0398e-5`). Trong the gioi phan ung, ego di cham/phanh som lam thay doi khe chuyen lan va phan ung xe sau; mot num cuc bo khong bao dam rui ro tong the giam. Anh so san can nop: `evidence/shots/policy_ghost.png` voi bong mo baseline.

## 7. Tu mo phong ra duong that

1. `cutGap` median 14 m cua town D can thay bang trajectory tu camera/LiDAR tai diem nhap lan, do khoang cach luc xe bat dau chuyen lan. Neu median thuc nho hon, mo phong hien tai danh gia thap rui ro cut-in.
2. `pedLook = 0.90` can thay bang video gan xe buyt/vach qua duong, gan nhan nguoi co quan sat qua vat che truoc khi buoc ra. Neu ti le nhin thuc thap hon, rui ro `crosswalk_block` bi danh gia thap.
3. Xac suat duong uot 0.15 va `mu = 0.5/0.8` can thay bang log thoi tiet ket hop ABS/ESC, tire-road friction estimator va bao tri mat duong. Neu duong uot nhieu hon hoac ma sat thap hon, kha nang dung se bi danh gia qua lac quan.

## 8. Gioi han

Xac suat nay khong bao phu: (1) mang duong ngoai mot doan pho va mot giao lo; (2) hanh vi nguoi lai ngoai IDM/gap acceptance da lap trinh; (3) loi cam bien, dinh vi, nhan dien va do tre, ngoai che khuat boi xe buyt. Neu co them mot tuan, toi se quet nhieu hinh hoc duong, chen mo hinh noise/delay cam bien da hieu chuan va danh gia lai tren log trajectory thuc bang held-out scenario.

## 9. Rac roi cua toi (buoc G + chuong 10)

**Rac roi.** Xe dan dau L1 phanh khan cap khi ego cach 8-35 m; do giam toc 3.0-7.5 m/s2 trong 1-4 s (`hazard.json: hazards`, `space`). Day mo phong phanh do vat can bat ngo. Planner co the xu ly kem neu IDM phan ung muon hoac phanh khong du manh.

**Gia dinh.** `exposure = 0.05/trip` la gia dinh day hoc co chu dich stress test, khong phai tan suat da do; truoc trien khai phai thay bang fleet log su kien phanh/near-miss. Simulator loai deceleration vuot `mu*g`; 1,365/1,500 mau hop le, `accepted = 0.91` (`mine.json`).

**Ket qua.** Scene chinh khong va cham (`mine.json: exact.planner = []`). Baseline co 1 va cham `unattributed`, 0 `avoidable`, 0 `unavoidable`, 0 `low_speed`; policy moi khong co va cham. Ca hai co P(loi planner | hazard) point estimate 0 va Wilson `[0, 2.8065e-3]`; can tan suat moi chuyen la `1.4032e-4`. Ket qua dung la planner da xu ly tot hazard trong ngan sach nay, khong phai hazard co rui ro bang 0. Anh can nop: `evidence/shots/hazard_brake.png` tai luc L1 phanh.

`avoidable` la chuan lac quan theo mot huong vi oracle biet dung frame dau tien co the thay va phanh toi da ngay, nen co the dem nhieu hon kha nang cua planner that. Nguoc lai, oracle chi thu phanh ma khong danh lai, nen co the dem it hon nhung tinh huong mot planner day du co the tranh. Policy moi khong cai thien co the quan sat tren hazard nay vi baseline da xu ly duoc; cach sua cu the neu fleet log cho thay near-miss la them du doan phanh cua lead vehicle/jerk trigger va emergency braking theo TTC, sau do kiem thu lai tren TEST moi.

Toi khong tu lai scene nay; do do khong dua ra so san con nguoi khong co bang chung.
