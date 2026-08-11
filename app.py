import random
import streamlit as st

# --- 定義 ---
METALS = [
    {"name": "鉄塊", "power": 10},
    {"name": "鋼鉄塊", "power": 15},
    {"name": "ミスリル塊", "power": 25},
]

MAGICS = [
    {"name": "豪炎の結晶", "mult": 1.5},
    {"name": "蒼氷の結晶", "mult": 1.4},
    {"name": "雷光の結晶", "mult": 1.6},
    {"name": "涼風の結晶", "mult": 1.3},
]

# --- セッションステートの初期化 ---
if "state" not in st.session_state:
    st.session_state.state = "start"  # start, craft, battle, gameover, clear
    st.session_state.loop = 1
    st.session_state.metals = []
    st.session_state.magics = []
    st.session_state.bullets = None  # {"name": str, "total_damage": int, "count": int}
    st.session_state.enemy_hp = 0
    st.session_state.enemy_max_hp = 0
    st.session_state.enemy_count = 0


def start_game():
    st.session_state.state = "craft"
    st.session_state.loop = 1
    generate_materials()


def generate_materials():
    # ランダムに素材をドロップ
    st.session_state.metals = [random.choice(METALS) for _ in range(3)]
    st.session_state.magics = [random.choice(MAGICS) for _ in range(4)]
    st.session_state.bullets = None


def start_battle(selected_metal_idx, selected_magic_indices):
    metal = st.session_state.metals[selected_metal_idx]
    magic1 = st.session_state.magics[selected_magic_indices[0]]
    magic2 = st.session_state.magics[selected_magic_indices[1]]

    # 銃弾の計算: 金属基礎攻撃力 × 魔力倍率1 × 魔力倍率2 × 10発分
    single_damage = metal["power"] * magic1["mult"] * magic2["mult"]
    total_damage = int(single_damage * 10)
    bullet_name = f"{metal['name']} × {magic1['name']} & {magic2['name']}"

    st.session_state.bullets = {
        "name": bullet_name,
        "total_damage": total_damage,
        "count": 10,
    }

    # 敵の設定（ループが進むにつれて強力に）
    st.session_state.enemy_count = random.randint(1, 3) + (
        st.session_state.loop // 3
    )
    st.session_state.enemy_max_hp = 80 + (st.session_state.loop * 35)
    st.session_state.enemy_hp = st.session_state.enemy_max_hp

    st.session_state.state = "battle"


# --- 画面レイアウト ---
st.title("🔫 弾薬合成 ＆ バトルRPG")

# 進捗表示
if st.session_state.state in ["craft", "battle"]:
    st.markdown(f"### 📍 現在のステージ: **第 {st.session_state.loop} / 10 回**")
    st.progress(st.session_state.loop / 10)
    st.markdown("---")

# 1. スタート画面
if st.session_state.state == "start":
    st.markdown("### 【ゲームルール】")
    st.markdown(
        "* **合成フェーズ**: ドロップした「金属素材」1つと「魔力素材」2つを組み合わせて、強力な銃弾（10発）を合成します。"
    )
    st.markdown(
        "* **戦闘フェーズ**: 合成した銃弾を使って、次々に出現する敵を倒します。"
    )
    st.markdown("* **勝利条件**: 全10回のループを生き抜き、すべての敵を倒すこと！")
    if st.button("ゲームスタート", type="primary", use_container_width=True):
        start_game()
        st.rerun()

# 2. 合成フェーズ
elif st.session_state.state == "craft":
    st.subheader("🛠️ 合成フェーズ")
    st.write(
        "手に入れた素材から **金属素材 1つ** と **魔力素材 2つ** を選択してください。"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🧱 入手した金属素材")
        metal_options = [
            f"{m['name']} (基礎攻撃力: {m['power']})"
            for m in st.session_state.metals
        ]
        selected_metal_idx = st.radio(
            "金属素材を選ぶ（1つ）",
            range(len(metal_options)),
            format_func=lambda x: metal_options[x],
        )

    with col2:
        st.markdown("#### 🔮 入手した魔力素材")
        magic_options = [
            f"{m['name']} (倍率: x{m['mult']})"
            for m in st.session_state.magics
        ]
        selected_magic_indices = st.multiselect(
            "魔力素材を選ぶ（ちょうど2つ）",
            range(len(magic_options)),
            format_func=lambda x: magic_options[x],
            max_selections=2,
        )

    st.markdown("---")
    if len(selected_magic_indices) == 2:
        if st.button(
            "銃弾を合成して戦闘へ！", type="primary", use_container_width=True
        ):
            start_battle(selected_metal_idx, selected_magic_indices)
            st.rerun()
    else:
        st.warning("⚠️ 魔力素材を**ちょうど2つ**選択してください。")

# 3. 戦闘フェーズ
elif st.session_state.state == "battle":
    st.subheader("⚔️ 戦闘フェーズ")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.metric(label="敵の数", value=f"{st.session_state.enemy_count} 体")
    with col_e2:
        st.metric(
            label="敵の合計HP",
            value=f"{st.session_state.enemy_hp} / {st.session_state.enemy_max_hp}",
        )

    st.progress(
        max(
            0.0,
            min(
                1.0,
                st.session_state.enemy_hp / st.session_state.enemy_max_hp,
            ),
        )
    )

    st.info(
        f"🎯 使用する銃弾: **{st.session_state.bullets['name']}** (総威力: {st.session_state.bullets['total_damage']} / 10発)"
    )

    if st.button("銃弾を全弾発射して攻撃！", type="primary", use_container_width=True):
        damage = st.session_state.bullets["total_damage"]
        st.session_state.enemy_hp -= damage

        if st.session_state.enemy_hp <= 0:
            st.session_state.enemy_hp = 0
            if st.session_state.loop >= 10:
                st.session_state.state = "clear"
            else:
                st.session_state.state = "next_stage"
        else:
            st.session_state.state = "gameover"
        st.rerun()

# 4. ステージクリア画面（次へ）
elif st.session_state.state == "next_stage":
    st.success(f"🎉 第 {st.session_state.loop} ステージの敵を撃破しました！")

    if st.button("次のステージへ進む", type="primary", use_container_width=True):
        st.session_state.loop += 1
        generate_materials()
        st.session_state.state = "craft"
        st.rerun()

# 5. ゲームオーバー画面
elif st.session_state.state == "gameover":
    st.error("💥 敵のHPを削り切れず、返り討ちにあってしまった…！")
    st.write(
        f"到達ステージ: 第 {st.session_state.loop} ステージ（残敵HP: {st.session_state.enemy_hp}）"
    )

    if st.button("もう一度挑戦する", type="primary", use_container_width=True):
        start_game()
        st.rerun()

# 6. 完全クリア画面
elif st.session_state.state == "clear":
    st.balloons()
    st.success("🏆 おめでとうございます！全10ステージをクリアし、世界を救いました！")

    if st.button("タイトルに戻る", type="primary", use_container_width=True):
        st.session_state.state = "start"
        st.rerun()
