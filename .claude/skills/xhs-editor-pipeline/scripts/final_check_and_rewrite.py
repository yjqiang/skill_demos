"""
小红书文案后处理脚本：敏感词处理、emoji 注入、段落重组、字数限流。

此脚本在 LLM 生成文案之后运行，负责：
1. 敏感词/违禁词 → 拼音替换（如"赚钱"→"zhuan钱"）
2. 关键词匹配 → 自动注入 emoji
3. 段落重组 → 制造"呼吸感"排版
4. 数字列表符号升级 → "1." → "1️⃣"
5. 字数强制限流 → 超长截断 + 引导关注
"""

import re
import argparse

from pypinyin import pinyin, Style

# ====== 配置词库 ======

# 敏感词列表（会触发拼音替换以避免平台限流）
SENSITIVE_WORDS = ["赚钱", "第一", "最好", "私聊", "购买", "限时特惠"]

# emoji 关键词映射：在关键词后追加 emoji，每个关键词只处理一次
EMOJI_MAPPING = {
    "震惊": "😱",
    "哭": "😭",
    "注意": "💡",
    "推荐": "🌟",
    "干货": "📝",
    "省钱": "💰",
    "好用": "✨",
    "必入": "🔥",
}

# 数字到 emoji 的映射
NUM_EMOJI = {
    "1": "1️⃣", "2": "2️⃣", "3": "3️⃣",
    "4": "4️⃣", "5": "5️⃣", "6": "6️⃣",
    "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣",
}


def _replace_sensitive_word(text, word):
    """将敏感词的前半部分转为拼音，后半保留原字。"""
    py_list = pinyin(word, style=Style.NORMAL)
    py_word = "".join([seg[0] for seg in py_list])

    if len(word) > 2:
        half_py = len(py_word) // 2
        half_word = len(word) // 2
        replaced = f"{py_word[:half_py]}.{word[half_word:]}"
    else:
        # 2字词：第一个字转拼音首段，第二个字保留
        replaced = f"{py_word[:len(py_word)//2]}{word[1:]}"

    return text.replace(word, replaced)


def _inject_emojis(text):
    """为关键词追加对应 emoji，每个关键词只注入一次（去重）。"""
    injected = set()
    for keyword, emoji in EMOJI_MAPPING.items():
        if keyword in text and keyword not in injected:
            # 只替换第一次出现，避免同一关键词多次追加 emoji
            text = text.replace(keyword, f"{keyword}{emoji}", 1)
            injected.add(keyword)
    return text


def _restructure_paragraphs(text):
    """按句号、问号、感叹号切分，每 2 句换行制造呼吸感。"""
    sentences = re.split(r'([。？！\?!])', text)
    rebuilt = ""
    count = 0

    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i] + sentences[i + 1]
        rebuilt += sentence
        count += 1
        if count % 2 == 0:
            rebuilt += "\n\n"

    # 补上尾部（标点分割后可能的剩余）
    if len(sentences) % 2 != 0:
        rebuilt += sentences[-1]

    return rebuilt.strip()


def _upgrade_number_badges(text):
    """将行首或句首的 '1.' '2.' 等替换为 emoji 数字符号。

    只在数字前后不是数字时才替换，避免误伤年份（如 2024.）"""
    # 匹配：非数字边界 + 单个数字 + "." + 非数字边界
    def replace_badge(match):
        num = match.group(1)
        return NUM_EMOJI.get(num, f"{num}.") + " "

    # (?<!\d) 前面不是数字，(\d) 单个数字，\. 点号，(?!\d) 后面不是数字
    text = re.sub(r'(?<!\d)(\d)\.(?!\d)', replace_badge, text)
    return text


def _truncate(text, max_length=1000):
    """字数超限时截断并追加引导关注语。"""
    if len(text) <= max_length:
        return text

    suffix = "\n\n后面太精彩了放不下，【关注我】看下集！✨"
    return text[:max_length - len(suffix)] + suffix


def process_xiaohongshu_text(text, max_length=1000):
    """
    小红书文案处理主流程。
    """
    # 模块一：敏感词处理
    for word in SENSITIVE_WORDS:
        if word in text:
            text = _replace_sensitive_word(text, word)

    # 模块二：emoji 注入
    text = _inject_emojis(text)

    # 模块三：段落重组
    text = _restructure_paragraphs(text)

    # 模块四：数字列表符号升级
    text = _upgrade_number_badges(text)

    # 模块五：字数限流
    text = _truncate(text, max_length)

    return text


# ================= 命令行入口 =================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书内容处理器")
    parser.add_argument('--text', type=str, required=True, help="LLM 生成的文案文本")

    args = parser.parse_args()
    print("--- 原始文案 ---")
    print(args.text)
    print("\n--- 脚本处理后的文案 ---")
    result = process_xiaohongshu_text(args.text)
    print(result)
