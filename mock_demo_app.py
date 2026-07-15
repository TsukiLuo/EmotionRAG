"""
情绪识别与关怀助手 (API Mock Demo)
前端负责人 - 成员4 开发

调用成员3（单嵩然）设计的 Mock 接口 /v1/agent/analyze
实现图片上传 + 文本输入 -> 多模态情绪分析 -> 智能回复的完整交互流程
"""

import json
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# ============================================================
# 配置区：Mock 接口地址（成员3 单嵩然提供）
# ============================================================
# Apifox 本地 Mock 地址
MOCK_URL = "http://127.0.0.1:4523/m1/8571821-8348753-default/v1/agent/analyze"
# 如果 Apifox 云端 Mock 可用，也可以替换为：
# MOCK_URL = "https://mock.apifox.com/m1/8571821-8348753-default/v1/agent/analyze"


# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="情绪识别与关怀助手",
    page_icon="🎭",
    layout="wide",
)

st.title("🎭 情绪识别与关怀助手 (API Mock Demo)")
st.markdown("---")
st.markdown("上传一张人脸图片，输入你当前的心情描述，AI 将为你进行多模态情绪分析并给出关怀建议。")


# ============================================================
# 用户输入区
# ============================================================
col_upload, col_text = st.columns([1, 2])

with col_upload:
    st.subheader("📷 上传人脸图片")
    uploaded_file = st.file_uploader(
        "选择一张人脸图片",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        help="支持 JPG / PNG / BMP / WebP 格式",
    )

with col_text:
    st.subheader("✍️ 输入心情描述")
    mood_text = st.text_area(
        "描述你现在的心情",
        height=120,
        placeholder="例如：今天工作压力好大，感觉有点焦虑和疲惫……",
    )

    # 可选的用户ID
    user_id = st.text_input(
        "用户ID（可选）",
        placeholder="用于记录历史，可不填",
    )


# ============================================================
# 分析按钮
# ============================================================
st.markdown("")
if st.button("🚀 开始分析", use_container_width=True, type="primary"):

    # --- 输入校验 ---
    if not uploaded_file:
        st.error("⚠️ 请先上传一张人脸图片！")
        st.stop()

    if not mood_text.strip():
        st.error("⚠️ 请输入心情描述文本！")
        st.stop()

    # --- 构造请求 ---
    files = {
        "image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type),
    }
    data = {
        "text": mood_text.strip(),
    }
    if user_id.strip():
        data["user_id"] = user_id.strip()

    # --- 调用 Mock 接口 ---
    with st.spinner("正在调用多模态情绪分析接口..."):
        try:
            resp = requests.post(MOCK_URL, files=files, data=data, timeout=30)

            if resp.status_code != 200:
                st.error(f"❌ 接口返回错误状态码：HTTP {resp.status_code}")
                with st.expander("查看错误详情"):
                    st.code(resp.text, language="json")
                st.stop()

            result = resp.json()

        except requests.exceptions.ConnectionError:
            st.error("❌ 网络连接失败！请检查 Mock 接口地址是否可访问。")
            st.info(f"当前 Mock 地址：`{MOCK_URL}`")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("❌ 请求超时！接口响应时间过长。")
            st.stop()
        except json.JSONDecodeError:
            st.error("❌ 接口返回的内容不是有效的 JSON 格式！")
            st.code(resp.text[:2000], language="text")
            st.stop()
        except Exception as e:
            st.error(f"❌ 发生未知错误：{e}")
            st.stop()

    # --- 成功提示 ---
    if result.get("code") == 200:
        st.success("✅ 分析完成！")
    else:
        st.warning(f"⚠️ 接口返回非成功状态：code={result.get('code')}, msg={result.get('msg')}")

    # ============================================================
    # 结果展示区
    # ============================================================
    st.markdown("---")
    st.subheader("📊 分析结果")

    col_img, col_result = st.columns([1, 2])

    # --- 左列：展示上传的图片 ---
    with col_img:
        st.markdown("**上传的图片**")
        try:
            img = Image.open(BytesIO(uploaded_file.getvalue()))
            st.image(img, caption=uploaded_file.name, use_container_width=True)
        except Exception:
            st.image(uploaded_file, caption=uploaded_file.name)

    # --- 右列：展示分析结果和回复 ---
    with col_result:
        data_obj = result.get("data", {})

        # analysis 部分
        analysis = data_obj.get("analysis", {})

        st.markdown("**🔍 多模态情绪分析**")

        # 图片情绪分析
        image_emotion = analysis.get("image_emotion", {})
        if image_emotion:
            dominant = image_emotion.get("dominant_emotion", "未知")
            smile_intensity = image_emotion.get("au12_r_smile_intensity", "N/A")
            brow_lower = image_emotion.get("au04_r_brow_lower", "N/A")

            st.markdown(f"""
            | 分析维度 | 结果 |
            |---|---|
            | **主要情绪** | {dominant} |
            | **微笑强度 (AU12)** | {smile_intensity} |
            | **皱眉强度 (AU04)** | {brow_lower} |
            """)

        # 文本情感分析
        text_sentiment = analysis.get("text_sentiment", "未知")
        text_keywords = analysis.get("text_keywords", [])

        st.markdown(f"""
        | 分析维度 | 结果 |
        |---|---|
        | **文本情感倾向** | {text_sentiment} |
        | **关键词** | {"、".join(text_keywords) if text_keywords else "无"} |
        """)

        # 决策与回复
        st.markdown("---")
        st.markdown("**💡 系统决策**")

        decision = data_obj.get("decision", "未知")
        # 映射决策到可读描述
        decision_map = {
            "need_knowledge": "需要知识库检索（知识增强）",
            "no_need": "无需额外知识",
            "general_chat": "常规对话",
        }
        decision_desc = decision_map.get(decision, decision)
        st.info(f"决策结果：**{decision_desc}**")

        st.markdown("**🤖 系统回复**")
        reply = data_obj.get("reply", "")
        st.markdown(f"> {reply}")

        # 建议来源
        advice_source = data_obj.get("advice_source", "")
        if advice_source:
            st.caption(f"📎 建议来源：{advice_source}")

    # ============================================================
    # 调试区：完整 API 响应
    # ============================================================
    st.markdown("---")
    with st.expander("🔧 完整 API 响应 JSON（调试用）"):
        st.json(result)
