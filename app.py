import random
import time
import streamlit as st

# --- 定義（画像ファイルパスを指定） ---
METALS = [
    {"name": "鉄塊", "power": 10, "img": "images/metal_iron.png"},
    {"name": "鋼鉄塊", "power": 15, "img": "images/metal_steel.png"},
    {"name": "ミスリル塊", "power": 25, "img": "images/metal_mithril.png"},
]

MAGICS = [
    {"name": "豪炎の結晶", "mult": 1.5, "img": "images/magic_fire.png"},
    {"name": "蒼氷の結晶", "mult": 1.4, "img": "images/magic_ice.png"},
    {"name": "雷光の結晶", "mult": 1.6, "img": "images/magic_thunder.png"},
    {"name": "涼風の結晶", "mult": 1.3, "img": "images/magic_wind.png"},
    {"name": "月光の結晶", "mult": 1.5, "img": "images/magic_moon.png"},
    {"name": "闇夜の結晶", "mult": 1.7, "img": "images/magic_dark.png"},
]

# 敵リストの定義（画像パスを指定）
ENEMY_TYPES = [
    {"name": "オーク (高攻撃力)", "img": "images/enemy_orc.png", "trait": "attack", "atk": 25, "def": 5, "heal": 0, "evade": 0.05},
    {"name": "ゴーレム (高防御力)", "img": "images/enemy_golem.png", "trait": "defense", "atk": 10, "def": 15, "heal": 0, "evade": 0.0},
    {"name": "トレント (高回復力)", "img": "images/enemy_treant.png", "trait": "heal", "atk": 10, "def": 5, "heal": 15, "evade": 0.05},
    {"name": "ニンジャ (高回避率)", "img": "images/enemy_ninja.png", "trait": "evade", "atk": 15, "def": 2, "heal": 0, "evade": 0.35},
]

# --- セッションステートの初期化 ---
if "state" not in st.session_state:
    st.session_state.state = "start"  # start, craft, battle, gameover, clear
    st.session_state.loop = 1
    st.session_state.metals = []
    st.session_state.magics = []
    st.session_state.bullets = None
    st.session_state.enemies = []
    st.session_state.enemy_hp = 0
    st.session_state.enemy_max_hp = 0


def start_game():
    st.session_state.state = "craft"
    st.session_state.loop = 1
    generate_materials()


def generate_materials():
    st.session_state.metals = [random.choice(METALS) for _ in range(3)]
    # 4つの魔力素材をランダムドロップ（同じものが重複してドロップすることもある）
    st.session_state.magics = [random.choice(MAGICS) for _ in range(4)]
    st.session_state.bullets = None


# --- 属性結晶が同じ場合を含めた銃弾パターン ---
def get_bullet_info(metal, magic1, magic2):
    sorted_magics = sorted([magic1["name"], magic2["name"]])
    m1_name, m2_name = sorted_magics[0], sorted_magics[1]

    bullet_patterns = {
        # --- 鉄塊の組み合わせ（異属性） ---
        ("鉄塊", "蒼氷の結晶", "豪炎の結晶"): {"name": "鉄製 蒸気爆弾", "img": "images/bullet_iron_fire_ice.png", "pierce": 5, "dot": 8},
        ("鉄塊", "豪炎の結晶", "雷光の結晶"): {"name": "鉄製 爆雷弾", "img": "images/bullet_iron_fire_thunder.png", "pierce": 0, "dot": 15},
        ("鉄塊", "涼風の結晶", "豪炎の結晶"): {"name": "鉄製 熱風弾", "img": "images/bullet_iron_fire_wind.png", "pierce": 2, "dot": 10},
        ("鉄塊", "月光の結晶", "豪炎の結晶"): {"name": "鉄製 陽炎弾", "img": "images/bullet_iron_fire_moon.png", "pierce": 4, "dot": 12},
        ("鉄塊", "豪炎の結晶", "闇夜の結晶"): {"name": "鉄製 冥火弾", "img": "images/bullet_iron_fire_dark.png", "pierce": 6, "dot": 18},
        ("鉄塊", "蒼氷の結晶", "雷光の結晶"): {"name": "鉄製 凍雷弾", "img": "images/bullet_iron_ice_thunder.png", "pierce": 8, "dot": 5},
        ("鉄塊", "涼風の結晶", "蒼氷の結晶"): {"name": "鉄製 吹雪弾", "img": "images/bullet_iron_ice_wind.png", "pierce": 3, "dot": 5},
        ("鉄塊", "月光の結晶", "蒼氷の結晶"): {"name": "鉄製 霊水弾", "img": "images/bullet_iron_ice_moon.png", "pierce": 5, "dot": 7},
        ("鉄塊", "蒼氷の結晶", "闇夜の結晶"): {"name": "鉄製 幽氷弾", "img": "images/bullet_iron_ice_dark.png", "pierce": 7, "dot": 10},
        ("鉄塊", "涼風の結晶", "雷光の結晶"): {"name": "鉄製 嵐弾", "img": "images/bullet_iron_thunder_wind.png", "pierce": 0, "dot": 12},
        ("鉄塊", "月光の結晶", "雷光の結晶"): {"name": "鉄製 閃光弾", "img": "images/bullet_iron_thunder_moon.png", "pierce": 10, "dot": 6},
        ("鉄塊", "闇夜の結晶", "雷光の結晶"): {"name": "鉄製 黒雷弾", "img": "images/bullet_iron_thunder_dark.png", "pierce": 8, "dot": 20},
        ("鉄塊", "月光の結晶", "涼風の結晶"): {"name": "鉄製 幻風弾", "img": "images/bullet_iron_wind_moon.png", "pierce": 3, "dot": 8},
        ("鉄塊", "涼風の結晶", "闇夜の結晶"): {"name": "鉄製 陰風弾", "img": "images/bullet_iron_wind_dark.png", "pierce": 4, "dot": 14},
        ("鉄塊", "月光の結晶", "闇夜の結晶"): {"name": "鉄製 混沌弾", "img": "images/bullet_iron_moon_dark.png", "pierce": 12, "dot": 15},

        # --- 鉄塊の組み合わせ（同属性） ---
        ("鉄塊", "豪炎の結晶", "豪炎の結晶"): {"name": "鉄製 爆炎弾", "img": "images/bullet_iron_fire_fire.png", "pierce": 2, "dot": 20},
        ("鉄塊", "蒼氷の結晶", "蒼氷の結晶"): {"name": "鉄製 氷結弾", "img": "images/bullet_iron_ice_ice.png", "pierce": 6, "dot": 6},
        ("鉄塊", "雷光の結晶", "雷光の結晶"): {"name": "鉄製 電磁弾", "img": "images/bullet_iron_thunder_thunder.png", "pierce": 4, "dot": 25},
        ("鉄塊", "涼風の結晶", "涼風の結晶"): {"name": "鉄製 旋風弾", "img": "images/bullet_iron_wind_wind.png", "pierce": 1, "dot": 10},
        ("鉄塊", "月光の結晶", "月光の結晶"): {"name": "鉄製 月光弾", "img": "images/bullet_iron_moon_moon.png", "pierce": 8, "dot": 12},
        ("鉄塊", "闇夜の結晶", "闇夜の結晶"): {"name": "鉄製 影縫弾", "img": "images/bullet_iron_dark_dark.png", "pierce": 10, "dot": 30},

        # --- 鋼鉄塊の組み合わせ（異属性） ---
        ("鋼鉄塊", "蒼氷の結晶", "豪炎の結晶"): {"name": "鋼鉄製 蒸気爆弾", "img": "images/bullet_steel_fire_ice.png", "pierce": 10, "dot": 10},
        ("鋼鉄塊", "豪炎の結晶", "雷光の結晶"): {"name": "鋼鉄製 爆雷弾", "img": "images/bullet_steel_fire_thunder.png", "pierce": 5, "dot": 20},
        ("鋼鉄塊", "涼風の結晶", "豪炎の結晶"): {"name": "鋼鉄製 熱風弾", "img": "images/bullet_steel_fire_wind.png", "pierce": 8, "dot": 12},
        ("鋼鉄塊", "月光の結晶", "豪炎の結晶"): {"name": "鋼鉄製 陽炎弾", "img": "images/bullet_steel_fire_moon.png", "pierce": 10, "dot": 15},
        ("鋼鉄塊", "豪炎の結晶", "闇夜の結晶"): {"name": "鋼鉄製 冥火弾", "img": "images/bullet_steel_fire_dark.png", "pierce": 12, "dot": 22},
        ("鋼鉄塊", "蒼氷の結晶", "雷光の結晶"): {"name": "鋼鉄製 凍雷弾", "img": "images/bullet_steel_ice_thunder.png", "pierce": 15, "dot": 8},
        ("鋼鉄塊", "涼風の結晶", "蒼氷の結晶"): {"name": "鋼鉄製 吹雪弾", "img": "images/bullet_steel_ice_wind.png", "pierce": 6, "dot": 8},
        ("鋼鉄塊", "月光の結晶", "蒼氷の結晶"): {"name": "鋼鉄製 霊水弾", "img": "images/bullet_steel_ice_moon.png", "pierce": 11, "dot": 10},
        ("鋼鉄塊", "蒼氷の結晶", "闇夜の結晶"): {"name": "鋼鉄製 幽氷弾", "img": "images/bullet_steel_ice_dark.png", "pierce": 14, "dot": 13},
        ("鋼鉄塊", "涼風の結晶", "雷光の結晶"): {"name": "鋼鉄製 嵐弾", "img": "images/bullet_steel_thunder_wind.png", "pierce": 4, "dot": 16},
        ("鋼鉄塊", "月光の結晶", "雷光の結晶"): {"name": "鋼鉄製 閃光弾", "img": "images/bullet_steel_thunder_moon.png", "pierce": 16, "dot": 9},
        ("鋼鉄塊", "闇夜の結晶", "雷光の結晶"): {"name": "鋼鉄製 黒雷弾", "img": "images/bullet_steel_thunder_dark.png", "pierce": 15, "dot": 25},
        ("鋼鉄塊", "月光の結晶", "涼風の結晶"): {"name": "鋼鉄製 幻風弾", "img": "images/bullet_steel_wind_moon.png", "pierce": 8, "dot": 11},
        ("鋼鉄塊", "涼風の結晶", "闇夜の結晶"): {"name": "鋼鉄製 陰風弾", "img": "images/bullet_steel_wind_dark.png", "pierce": 10, "dot": 18},
        ("鋼鉄塊", "月光の結晶", "闇夜の結晶"): {"name": "鋼鉄製 混沌弾", "img": "images/bullet_steel_moon_dark.png", "pierce": 18, "dot": 20},

        # --- 鋼鉄塊の組み合わせ（同属性） ---
        ("鋼鉄塊", "豪炎の結晶", "豪炎の結晶"): {"name": "鋼鉄製 爆炎弾", "img": "images/bullet_steel_fire_fire.png", "pierce": 6, "dot": 25},
        ("鋼鉄塊", "蒼氷の結晶", "蒼氷の結晶"): {"name": "鋼鉄製 氷結弾", "img": "images/bullet_steel_ice_ice.png", "pierce": 12, "dot": 10},
        ("鋼鉄塊", "雷光の結晶", "雷光の結晶"): {"name": "鋼鉄製 電磁弾", "img": "images/bullet_steel_thunder_thunder.png", "pierce": 10, "dot": 35},
        ("鋼鉄塊", "涼風の結晶", "涼風の結晶"): {"name": "鋼鉄製 旋風弾", "img": "images/bullet_steel_wind_wind.png", "pierce": 4, "dot": 15},
        ("鋼鉄塊", "月光の結晶", "月光の結晶"): {"name": "鋼鉄製 月光弾", "img": "images/bullet_steel_moon_moon.png", "pierce": 14, "dot": 18},
        ("鋼鉄塊", "闇夜の結晶", "闇夜の結晶"): {"name": "鋼鉄製 影縫弾", "img": "images/bullet_steel_dark_dark.png", "pierce": 16, "dot": 40},

        # --- ミスリル塊の組み合わせ（異属性） ---
        ("ミスリル塊", "蒼氷の結晶", "豪炎の結晶"): {"name": "ミスリル製 蒸気爆弾", "img": "images/bullet_mithril_fire_ice.png", "pierce": 20, "dot": 15},
        ("ミスリル塊", "豪炎の結晶", "雷光の結晶"): {"name": "ミスリル製 爆雷弾", "img": "images/bullet_mithril_fire_thunder.png", "pierce": 10, "dot": 30},
        ("ミスリル塊", "涼風の結晶", "豪炎の結晶"): {"name": "ミスリル製 熱風弾", "img": "images/bullet_mithril_fire_wind.png", "pierce": 15, "dot": 20},
        ("ミスリル塊", "月光の結晶", "豪炎の結晶"): {"name": "ミスリル製 陽炎弾", "img": "images/bullet_mithril_fire_moon.png", "pierce": 18, "dot": 22},
        ("ミスリル塊", "豪炎の結晶", "闇夜の結晶"): {"name": "ミスリル製 冥火弾", "img": "images/bullet_mithril_fire_dark.png", "pierce": 22, "dot": 35},
        ("ミスリル塊", "蒼氷の結晶", "雷光の結晶"): {"name": "ミスリル製 凍雷弾", "img": "images/bullet_mithril_ice_thunder.png", "pierce": 25, "dot": 12},
        ("ミスリル塊", "涼風の結晶", "蒼氷の結晶"): {"name": "ミスリル製 吹雪弾", "img": "images/bullet_mithril_ice_wind.png", "pierce": 12, "dot": 12},
        ("ミスリル塊", "月光の結晶", "蒼氷の結晶"): {"name": "ミスリル製 霊水弾", "img": "images/bullet_mithril_ice_moon.png", "pierce": 20, "dot": 16},
        ("ミスリル塊", "蒼氷の結晶", "闇夜の結晶"): {"name": "ミスリル製 幽氷弾", "img": "images/bullet_mithril_ice_dark.png", "pierce": 24, "dot": 20},
        ("ミスリル塊", "涼風の結晶", "雷光の結晶"): {"name": "ミスリル製 嵐弾", "img": "images/bullet_mithril_thunder_wind.png", "pierce": 8, "dot": 25},
        ("ミスリル塊", "月光の結晶", "雷光の結晶"): {"name": "ミスリル製 閃光弾", "img": "images/bullet_mithril_thunder_moon.png", "pierce": 28, "dot": 15},
        ("ミスリル塊", "闇夜の結晶", "雷光の結晶"): {"name": "ミスリル製 黒雷弾", "img": "images/bullet_mithril_thunder_dark.png", "pierce": 25, "dot": 40},
        ("ミスリル塊", "月光の結晶", "涼風の結晶"): {"name": "ミスリル製 幻風弾", "img": "images/bullet_mithril_wind_moon.png", "pierce": 15, "dot": 18},
        ("ミスリル塊", "涼風の結晶", "闇夜の結晶"): {"name": "ミスリル製 陰風弾", "img": "images/bullet_mithril_wind_dark.png", "pierce": 18, "dot": 28},
        ("ミスリル塊", "月光の結晶", "闇夜の結晶"): {"name": "ミスリル製 混沌弾", "img": "images/bullet_mithril_moon_dark.jpg", "pierce": 30, "dot": 30},

        # --- ミスリル塊の組み合わせ（同属性） ---
        ("ミスリル塊", "豪炎の結晶", "豪炎の結晶"): {"name": "ミスリル製 爆炎弾", "img": "images/bullet_mithril_fire_fire.png", "pierce": 12, "dot": 40},
        ("ミスリル塊", "蒼氷の結晶", "蒼氷の結晶"): {"name": "ミスリル製 氷結弾", "img": "images/bullet_mithril_ice_ice.png", "pierce": 20, "dot": 18},
        ("ミスリル塊", "雷光の結晶", "雷光の結晶"): {"name": "ミスリル製 電磁弾", "img": "images/bullet_mithril_thunder_thunder.png", "pierce": 18, "dot": 50},
        ("ミスリル塊", "涼風の結晶", "涼風の結晶"): {"name": "ミスリル製 旋風弾", "img": "images/bullet_mithril_wind_wind.png", "pierce": 8, "dot": 25},
        ("ミスリル塊", "月光の結晶", "月光の結晶"): {"name": "ミスリル製 月光弾", "img": "images/bullet_mithril_moon_moon.png", "pierce": 24, "dot": 30},
        ("ミスリル塊", "闇夜の結晶", "闇夜の結晶"): {"name": "ミスリル製 影縫弾", "img": "images/bullet_mithril_dark_dark.png", "pierce": 28, "dot": 60},
    }

    key = (metal["name"], m1_name, m2_name)
    return bullet_patterns.get(
        key,
        {
            "name": f"{metal['name']} × {m1_name}&{m2_name}",
            "img": metal["img"],
            "pierce": 5,
            "dot": 5,
        },
    )


def start_battle(selected_metal_idx, selected_magic_idx1, selected_magic_idx2):
    metal = st.session_state.metals[selected_metal_idx]
    magic1 = st.session_state.magics[selected_magic_idx1]
    magic2 = st.session_state.magics[selected_magic_idx2]

    b_info = get_bullet_info(metal, magic1, magic2)
    
    # 基本の威力計算
    base_damage_mult = magic1["mult"] * magic2["mult"]
    
    # 同属性結晶が選択された場合、個数に応じたボーナス倍率を加算
    # （例: 同じ名前の結晶であればボーナスとして倍率に +0.3 または 1.2倍）
    resonance_bonus = 0.0
    if magic1["name"] == magic2["name"]:
        resonance_bonus = 0.4  # 同属性同盟ボーナス
        b_info["name"] = f"共鳴・{b_info['name']}"
        b_info["pierce"] += 5
        b_info["dot"] += 5

    single_damage = int(metal["power"] * (base_damage_mult + resonance_bonus))

    st.session_state.bullets = {
        "name": b_info["name"],
        "img": b_info["img"],
        "single_damage": single_damage,
        "pierce": b_info["pierce"],
        "dot": b_info["dot"],
        "count": 10,
    }

    num_enemies = random.randint(1, 2) + (st.session_state.loop // 4)
    st.session_state.enemies = [
        random.choice(ENEMY_TYPES) for _ in range(num_enemies)
    ]

    base_hp = 120 + (st.session_state.loop * 45)
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
    st.markdown("### 【ゲームルール & 戦略ヒント】")
    st.markdown("* **合成フェーズ**: 銃弾ごとに**「貫通力」**や**「継続ダメージ」**の性能が異なります。")
    st.markdown("* **共鳴ボーナス**: 同じ属性の結晶を2つ選んで合成すると、**共鳴効果**により威力が大幅にアップします！")
    st.markdown("""* **敵の特性**: 
  * 🗿 **高防御力**: 貫通力の高い弾が有効
  * 🌳 **高回復力**: 毎ターンHPを削る「継続ダメージ」弾で相殺
  * 🥷 **高回避率**: 確実に当てるための工夫が必要
  * 🐗 **高攻撃力**: 短期決戦で素早く倒すべし！""")
    if st.button("ゲームスタート", type="primary", use_container_width=True):
        start_game()
        st.rerun()

# 2. 合成フェーズ
elif st.session_state.state == "craft":
    st.subheader("🛠️ 合成フェーズ")
    st.write("手に入れた素材から **金属素材 1つ** と **魔力素材 2つ** を選択してください。（同じ属性の結晶を選ぶと共鳴ボーナス！）")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🧱 入手した金属素材")
        for i, m in enumerate(st.session_state.metals):
            col_img, col_txt = st.columns([1, 4])
            with col_img:
                st.image(m["img"], width=100)
            with col_txt:
                st.write(f"**{m['name']}** (基礎攻撃力: {m['power']})")
        
        selected_metal_idx = st.radio(
            "金属素材を選ぶ（1つ）",
            range(len(st.session_state.metals)),
            format_func=lambda x: st.session_state.metals[x]["name"],
        )

    with col2:
        st.markdown("#### 🔮 入手した魔力素材（ドロップ）")
        for i, mg in enumerate(st.session_state.magics):
            col_img, col_txt = st.columns([1, 4])
            with col_img:
                st.image(mg["img"], width=100)
            with col_txt:
                st.write(f"[{i+1}] **{mg['name']}** (倍率: x{mg['mult']})")

        # 同じ属性の結晶も含めて2つ選べるように独立したセレクトボックスを用意
        magic_choices = range(len(st.session_state.magics))
        magic_format = lambda x: f"[{x+1}] {st.session_state.magics[x]['name']} (x{st.session_state.magics[x]['mult']})"
        
        selected_magic_idx1 = st.selectbox("魔力素材 1つ目を選ぶ", magic_choices, format_func=magic_format, index=0)
        selected_magic_idx2 = st.selectbox("魔力素材 2つ目を選ぶ", magic_choices, format_func=magic_format, index=min(1, len(magic_choices)-1))

    # プレビュー表示
    m_preview = st.session_state.metals[selected_metal_idx]
    mg1_preview = st.session_state.magics[selected_magic_idx1]
    mg2_preview = st.session_state.magics[selected_magic_idx2]

    preview_b_info = get_bullet_info(m_preview, mg1_preview, mg2_preview)
    
    preview_mult = mg1_preview["mult"] * mg2_preview["mult"]
    if mg1_preview["name"] == mg2_preview["name"]:
        preview_mult += 0.4
        preview_b_info["name"] = f"共鳴・{preview_b_info['name']}"

    preview_damage = int(m_preview["power"] * preview_mult * 10)

    st.markdown("---")
    st.markdown("#### 🔍 合成プレビュー")
    
    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        st.image(preview_b_info["img"], width=150)
    with col_p2:
        st.markdown(f"### **{preview_b_info['name']}**")
        if mg1_preview["name"] == mg2_preview["name"]:
            st.success("✨ 【同属性共鳴ボーナス発動！】 威力・貫通力・継続ダメージが上昇します！")
        st.write(f"予測総威力: **{preview_damage}** （1発あたり約 {int(preview_damage/10)} × 10発）")
        st.write(f"⚔️ **貫通力**: {preview_b_info['pierce'] if mg1_preview['name'] != mg2_preview['name'] else preview_b_info['pierce']} | 🔥 **継続ダメージ**: {preview_b_info['dot']}")

    st.markdown("---")
    if st.button("銃弾を合成して戦闘へ！", type="primary", use_container_width=True):
        start_battle(selected_metal_idx, selected_magic_idx1, selected_magic_idx2)
        st.rerun()

# 3. 戦闘フェーズ
elif st.session_state.state == "battle":
    st.subheader("⚔️ 戦闘フェーズ")

    # 複数出現する敵の表示（st.imageを使用）
    st.markdown("#### 👾 襲い来る敵グループ（特性持ち）")
    enemy_cols = st.columns(len(st.session_state.enemies))
    for idx, enemy in enumerate(st.session_state.enemies):
        with enemy_cols[idx]:
            st.image(enemy["img"], width=120)
            st.markdown(f"<div style='text-align: center;'><b>{enemy['name']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 0.8rem; color: gray;'>ATK:{enemy['atk']} / DEF:{enemy['def']} / 回復:{enemy['heal']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    hp_metric_placeholder = st.empty()
    progress_placeholder = st.empty()
    status_msg_placeholder = st.empty()

    hp_metric_placeholder.metric(
        label="敵チームの合計HP",
        value=f"{st.session_state.enemy_hp} / {st.session_state.enemy_max_hp}",
    )
    progress_placeholder.progress(
        max(0.0, min(1.0, st.session_state.enemy_hp / st.session_state.enemy_max_hp))
    )

    # 装着中の銃弾情報を画像付きで表示
    col_b1, col_b2 = st.columns([1, 5])
    with col_b1:
        st.image(st.session_state.bullets["img"], width=150)
    with col_b2:
        st.info(
            f"🎯 装着中の銃弾: **{st.session_state.bullets['name']}** "
            f"(1発威力: {st.session_state.bullets['single_damage']} | 貫通: {st.session_state.bullets['pierce']} | 継続: {st.session_state.bullets['dot']})"
        )

    if st.button("銃弾を連射して攻撃を開始！", type="primary", use_container_width=True):
        avg_def = sum([e["def"] for e in st.session_state.enemies]) / len(st.session_state.enemies)
        avg_heal = sum([e["heal"] for e in st.session_state.enemies]) / len(st.session_state.enemies)
        avg_evade = sum([e["evade"] for e in st.session_state.enemies]) / len(st.session_state.enemies)

        for shot in range(1, 11):
            if st.session_state.enemy_hp <= 0:
                break

            if random.random() < avg_evade:
                status_msg_placeholder.warning(f"💨 【{shot}発目】 敵に回避されてしまった…！ (ダメージ 0)")
                time.sleep(0.3)
                continue

            effective_def = max(0, avg_def - st.session_state.bullets["pierce"])
            hit_damage = max(1, st.session_state.bullets["single_damage"] - effective_def)
            total_shot_damage = hit_damage + st.session_state.bullets["dot"]
            total_shot_damage = max(1, total_shot_damage - int(avg_heal))

            st.session_state.enemy_hp = max(0, st.session_state.enemy_hp - total_shot_damage)

            hp_metric_placeholder.metric(
                label="敵チームの合計HP",
                value=f"{st.session_state.enemy_hp} / {st.session_state.enemy_max_hp}",
            )
            progress_placeholder.progress(
                max(0.0, min(1.0, st.session_state.enemy_hp / st.session_state.enemy_max_hp))
            )
            status_msg_placeholder.warning(
                f"🔥 【{shot}発目】 命中！貫通・継続効果を含め {total_shot_damage} のダメージ！（残りHP: {st.session_state.enemy_hp}）"
            )
            time.sleep(0.3)

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
    st.write(f"到達ステージ: 第 {st.session_state.loop} ステージ（残敵HP: {st.session_state.enemy_hp}）")

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
