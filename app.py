import random
import time
import streamlit as st

# --- 定義 ---
METALS = [
    {"name": "鉄塊", "power": 10, "img": "⚙️"},
    {"name": "鋼鉄塊", "power": 15, "img": "🔩"},
    {"name": "ミスリル塊", "power": 25, "img": "✨"},
]

MAGICS = [
    {"name": "豪炎の結晶", "mult": 1.5, "img": "🔥"},
    {"name": "蒼氷の結晶", "mult": 1.4, "img": "❄️"},
    {"name": "雷光の結晶", "mult": 1.6, "img": "⚡"},
    {"name": "涼風の結晶", "mult": 1.3, "img": "🍃"},
]

# 敵リストの定義
ENEMY_TYPES = [
    {"name": "スライム", "img": "🟢"},
    {"name": "ゴブリン", "img": "👺"},
    {"name": "オーク", "img": "🐗"},
    {"name": "ドラゴン", "img": "🐉"},
]

# --- セッションステートの初期化 ---
if "state" not in st.session_state:
    st.session_state.state = "start"  # start, craft, battle, gameover, clear
    st.session_state.loop = 1
    st.session_state.metals = []
    st.session_state.magics = []
    st.session_state.bullets = None
    st.session_state.enemies = []  # リストから選ばれた複数の敵
    st.session_state.enemy_hp = 0
    st.session_state.enemy_max_hp = 0


def start_game():
    st.session_state.state = "craft"
    st.session_state.loop = 1
    generate_materials()


def generate_materials():
    st.session_state.metals = [random.choice(METALS) for _ in range(3)]
    st.session_state.magics = [random.choice(MAGICS) for _ in range(4)]
    st.session_state.bullets = None


# --- 修正・追加する定義と関数 ---

# 魔力素材の組み合わせ（6通り）を判定して18通りの銃弾情報を返す関数
def get_bullet_info(metal, magic1, magic2):
    # 魔力2つの名前をソートして順序に依存しないようにする（6通りを網羅）
    sorted_magics = sorted([magic1["name"], magic2["name"]])
    m1_name, m2_name = sorted_magics[0], sorted_magics[1]

    # 18通り（金属3種 × 魔力ペア6種）の固有名称と画像アイコンの定義
    bullet_patterns = {
        ("鉄塊", "蒼氷の結晶", "豪炎の結晶"): {
            "name": "鉄製 蒸気爆弾",
            "img": "images/steal_fire_ice",
        },
        ("鉄塊", "豪炎の結晶", "雷光の結晶"): {
            "name": "鉄製 爆雷弾",
            "img": "images/steal_fire_thunder",
        },
        ("鉄塊", "涼風の結晶", "豪炎の結晶"): {
            "name": "鉄製 熱風弾",
            "img": "images/steal_fire_wind",
        },
        ("鉄塊", "蒼氷の結晶", "雷光の結晶"): {
            "name": "鉄製 凍雷弾",
            "img": "images/steal_ice_thunder",
        },
        ("鉄塊", "涼風の結晶", "蒼氷の結晶"): {
            "name": "鉄製 吹雪弾",
            "img": "images/steal_ice_wind",
        },
        ("鉄塊", "涼風の結晶", "雷光の結晶"): {
            "name": "鉄製 嵐弾",
            "img": "images/steal_thunder_wind",
        },
        ("鋼鉄塊", "蒼氷の結晶", "豪炎の結晶"): {
            "name": "鋼鉄製 蒸気爆弾",
            "img": "🔩🔥❄️",
        },
        ("鋼鉄塊", "豪炎の結晶", "雷光の結晶"): {
            "name": "鋼鉄製 爆雷弾",
            "img": "🔩🔥⚡",
        },
        ("鋼鉄塊", "涼風の結晶", "豪炎の結晶"): {
            "name": "鋼鉄製 熱風弾",
            "img": "🔩🔥🍃",
        },
        ("鋼鉄塊", "蒼氷の結晶", "雷光の結晶"): {
            "name": "鋼鉄製 凍雷弾",
            "img": "🔩❄️⚡",
        },
        ("鋼鉄塊", "涼風の結晶", "蒼氷の結晶"): {
            "name": "鋼鉄製 吹雪弾",
            "img": "🔩❄️🍃",
        },
        ("鋼鉄塊", "涼風の結晶", "雷光の結晶"): {
            "name": "鋼鉄製 嵐弾",
            "img": "🔩⚡🍃",
        },
        ("ミスリル塊", "蒼氷の結晶", "豪炎の結晶"): {
            "name": "ミスリル製 蒸気爆弾",
            "img": "✨🔥❄️",
        },
        ("ミスリル塊", "豪炎の結晶", "雷光の結晶"): {
            "name": "ミスリル製 爆雷弾",
            "img": "✨🔥⚡",
        },
        ("ミスリル塊", "涼風の結晶", "豪炎の結晶"): {
            "name": "ミスリル製 熱風弾",
            "img": "✨🔥🍃",
        },
        ("ミスリル塊", "蒼氷の結晶", "雷光の結晶"): {
            "name": "ミスリル製 凍雷弾",
            "img": "✨❄️⚡",
        },
        ("ミスリル塊", "涼風の結晶", "蒼氷の結晶"): {
            "name": "ミスリル製 吹雪弾",
            "img": "✨❄️🍃",
        },
        ("ミスリル塊", "涼風の結晶", "雷光の結晶"): {
            "name": "ミスリル製 嵐弾",
            "img": "✨⚡🍃",
        },
    }

    key = (metal["name"], m1_name, m2_name)
    return bullet_patterns.get(
        key,
        {
            "name": f"{metal['name']} × {m1_name}&{m2_name}",
            "img": f"🎯{metal['img']}",
        },
    )


def start_battle(selected_metal_idx, selected_magic_indices):
    metal = st.session_state.metals[selected_metal_idx]
    magic1 = st.session_state.magics[selected_magic_indices[0]]
    magic2 = st.session_state.magics[selected_magic_indices[1]]

    # 18通りに対応する固有の銃弾データを取得
    b_info = get_bullet_info(metal, magic1, magic2)

    # 1発あたりのダメージ計算
    single_damage = int(metal["power"] * magic1["mult"] * magic2["mult"])

    st.session_state.bullets = {
        "name": b_info["name"],
        "img": b_info["img"],
        "single_damage": single_damage,
        "count": 10,
    }

    # 敵リストから複数選出
    num_enemies = random.randint(1, 2) + (st.session_state.loop // 4)
    st.session_state.enemies = [
        random.choice(ENEMY_TYPES) for _ in range(num_enemies)
    ]

    base_hp = 100 + (st.session_state.loop * 40)
    st.session_state.enemy_max_hp = base_hp
    st.session_state.enemy_hp = base_hp

    st.session_state.state = "battle"


# --- 画面レイアウト ---
st.title("🔫 弾薬合成 ＆ バトルRPG")

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
        "* **戦闘フェーズ**: 1発ずつ銃弾を撃ち込み、現れた複数の敵を倒します。"
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
            f"{m['img']} {m['name']} (基礎攻撃力: {m['power']})"
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
            f"{m['img']} {m['name']} (倍率: x{m['mult']})"
            for m in st.session_state.magics
        ]
        selected_magic_indices = st.multiselect(
            "魔力素材を選ぶ（ちょうど2つ）",
            range(len(magic_options)),
            format_func=lambda x: magic_options[x],
            max_selections=2,
        )

    # プレビュー表示
    # 合成プレビュー表示部分
    if len(selected_magic_indices) == 2:
        m_preview = st.session_state.metals[selected_metal_idx]
        mg1_preview = st.session_state.magics[selected_magic_indices[0]]
        mg2_preview = st.session_state.magics[selected_magic_indices[1]]

        # 18通りのプレビュー情報を取得
        preview_b_info = get_bullet_info(m_preview, mg1_preview, mg2_preview)
        preview_damage = int(
            m_preview["power"]
            * mg1_preview["mult"]
            * mg2_preview["mult"]
            * 10
        )

        st.markdown("---")
        st.markdown("#### 🔍 合成プレビュー")
        st.markdown(
            f"### {preview_b_info['img']} **{preview_b_info['name']}**"
        )
        st.write(
            f"予測総威力: **{preview_damage}** （1発あたり約 {int(preview_damage/10)} × 10発）"
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

    # 複数出現する敵の表示
    st.markdown("#### 👾 襲い来る敵グループ")
    enemy_cols = st.columns(len(st.session_state.enemies))
    for idx, enemy in enumerate(st.session_state.enemies):
        with enemy_cols[idx]:
            st.markdown(
                f"<div style='text-align: center; font-size: 2rem;'>{enemy['img']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align: center;'>{enemy['name']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ステータス表示エリア
    hp_metric_placeholder = st.empty()
    progress_placeholder = st.empty()
    status_msg_placeholder = st.empty()

    hp_metric_placeholder.metric(
        label="敵チームの合計HP",
        value=f"{st.session_state.enemy_hp} / {st.session_state.enemy_max_hp}",
    )
    progress_placeholder.progress(
        max(
            0.0,
            min(
                1.0,
                st.session_state.enemy_hp / st.session_state.enemy_max_hp,
            ),
        )
    )

    st.info(
        f"🎯 装着中の銃弾: {st.session_state.bullets['img']} **{st.session_state.bullets['name']}** (1発威力: {st.session_state.bullets['single_damage']})"
    )

    if st.button("銃弾を連射して攻撃を開始！", type="primary", use_container_width=True):
        # 1発ずつ消費する演出（ループ処理）
        for shot in range(1, 11):
            if st.session_state.enemy_hp <= 0:
                break

            damage = st.session_state.bullets["single_damage"]
            st.session_state.enemy_hp = max(0, st.session_state.enemy_hp - damage)

            # 画面をリアルタイムに更新
            hp_metric_placeholder.metric(
                label="敵チームの合計HP",
                value=f"{st.session_state.enemy_hp} / {st.session_state.enemy_max_hp}",
            )
            progress_placeholder.progress(
                max(
                    0.0,
                    min(
                        1.0,
                        st.session_state.enemy_hp / st.session_state.enemy_max_hp,
                    ),
                )
            )
            status_msg_placeholder.warning(
                f"🔥 【{shot}発目】 弾丸が命中！ {damage} のダメージを与えた！（残りHP: {st.session_state.enemy_hp}）"
            )
            time.sleep(0.3)   # 1発ごとのウェイト（演出用）

        # 判定
        if st.session_state.enemy_hp <= 0:
            time.sleep(0.5)
            if st.session_state.loop >= 10:
                st.session_state.state = "clear"
            else:
                st.session_state.state = "next_stage"
        else:
            time.sleep(0.5)
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
