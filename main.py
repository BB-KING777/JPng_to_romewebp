import os
import urllib.parse
from pykakasi import kakasi
import MeCab
import re
import shutil
from PIL import Image

# MeCabとKakasiの初期化
try:
    tagger = MeCab.Tagger()
except RuntimeError:
    print("Error: MeCabを正しくインストールしてください。")
    print("Windowsユーザーは、MeCabの公式サイトからインストーラをダウンロードし、PATHを設定する必要があります。")
    exit()

# PyKakasiの設定
kks = kakasi()
kks.setMode('J', 'a')  # 漢字からローマ字
kks.setMode('H', 'a')  # ひらがなからローマ字
kks.setMode('K', 'a')  # カタカナからローマ字
kks.setMode('r', 'Hepburn')  # ヘボン式ローマ字
converter = kks.getConverter()

# 変換されたファイル名を保持するセット
converted_names = set()

# 画像変換対象の拡張子
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
WEBP_QUALITY = 80  # WebP品質設定（1-100）

def create_readable_filename(original_name, convert_to_webp=False):
    """
    日本語ファイル名をローマ字の可読ファイル名に変換する関数
    画像ファイルの場合はWebP変換も行う
    """
    global converted_names
    
    base_name, extension = os.path.splitext(original_name)
    
    # 画像ファイルをWebPに変換する場合
    if convert_to_webp and extension.lower() in IMAGE_EXTENSIONS:
        extension = '.webp'
    
    # 全角スペースや特殊文字を正規化
    base_name = base_name.replace('　', ' ').replace('*', '').strip()
    
    try:
        # PyKakasiで変換
        romanized_text = converter.do(base_name)
        
        # 文字列のクリーンアップ
        safe_name = re.sub(r'[^\w\-_.]', '_', romanized_text)  # 英数字、ハイフン、アンダースコア、ドット以外を_に
        safe_name = re.sub(r'_+', '_', safe_name)  # 連続するアンダースコアを1つに
        safe_name = safe_name.strip('_')  # 先頭末尾のアンダースコアを除去
        
        # 空文字列の場合は元のファイル名を使用
        if not safe_name:
            safe_name = "converted_file"
            
    except Exception as e:
        print(f"変換エラー ({base_name}): {e}")
        safe_name = "converted_file"
    
    # 重複チェック
    new_base_name = safe_name
    count = 1
    while new_base_name in converted_names:
        new_base_name = f"{safe_name}_{count}"
        count += 1
    converted_names.add(new_base_name)
    
    final_filename = new_base_name + extension.lower()
    
    return final_filename

def convert_image_to_webp(input_path, output_path, quality=WEBP_QUALITY):
    """
    画像をWebP形式に変換する
    """
    try:
        with Image.open(input_path) as img:
            # RGBAモードの場合はRGBに変換（WebPのために）
            if img.mode in ('RGBA', 'LA'):
                # 透明度を保持してWebPに変換
                img.save(output_path, 'WEBP', quality=quality, lossless=False)
            else:
                # RGB等の場合は通常の変換
                img.convert('RGB').save(output_path, 'WEBP', quality=quality, optimize=True)
        return True
    except Exception as e:
        print(f"画像変換エラー ({input_path}): {e}")
        return False

def find_target_files(directory_path):
    """
    変換対象のファイルを検索する
    """
    target_files = []
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # ファイルのみを対象とし、ディレクトリは除外
            if os.path.isfile(file_path):
                # 日本語文字またはスペースを含むファイルを対象とする
                if ' ' in filename or any('\u3000' <= char <= '\u9fff' for char in filename):
                    target_files.append(filename)
    
    except Exception as e:
        print(f"ディレクトリの読み取りエラー: {e}")
    
    return target_files

def preview_conversions(directory_path, target_files, enable_webp_conversion=False):
    """
    変換予定を表示する
    """
    conversions = []
    
    print("=== 変換予定のファイル ===")
    print()
    
    for filename in target_files:
        try:
            base_name, extension = os.path.splitext(filename)
            is_image = extension.lower() in IMAGE_EXTENSIONS
            
            # WebP変換を有効にし、かつ画像ファイルの場合
            convert_to_webp = enable_webp_conversion and is_image
            
            new_filename = create_readable_filename(filename, convert_to_webp)
            
            conversions.append({
                'old_name': filename,
                'new_name': new_filename,
                'convert_to_webp': convert_to_webp,
                'is_image': is_image
            })
            
            print(f"変更前: {filename}")
            print(f"変更後: {new_filename}")
            
            if convert_to_webp:
                print("  → 画像形式: WebPに変換")
            elif is_image and not enable_webp_conversion:
                print("  → 画像ファイル（WebP変換は無効）")
                
            print("-" * 50)
            
        except Exception as e:
            print(f"変換エラー ({filename}): {e}")
            print("-" * 50)
    
    return conversions

def rename_and_convert_files(directory_path, conversions):
    """
    実際にファイル名を変更し、必要に応じて画像を変換する
    """
    success_count = 0
    error_count = 0
    
    print("\n=== ファイル名変更・画像変換を実行中... ===")
    
    for conversion in conversions:
        old_name = conversion['old_name']
        new_name = conversion['new_name']
        convert_to_webp = conversion['convert_to_webp']
        
        try:
            old_path = os.path.join(directory_path, old_name)
            new_path = os.path.join(directory_path, new_name)
            
            # 新しいファイル名が既に存在する場合はスキップ
            if os.path.exists(new_path):
                print(f"スキップ: {new_name} は既に存在します")
                error_count += 1
                continue
            
            if convert_to_webp:
                # 画像をWebPに変換
                if convert_image_to_webp(old_path, new_path):
                    # 元のファイルを削除
                    os.remove(old_path)
                    print(f"成功（WebP変換）: {old_name} → {new_name}")
                    success_count += 1
                else:
                    # WebP変換に失敗した場合は通常のリネーム
                    os.rename(old_path, new_path)
                    print(f"WebP変換失敗・リネームのみ: {old_name} → {new_name}")
                    success_count += 1
            else:
                # 通常のファイル名変更
                os.rename(old_path, new_path)
                print(f"成功: {old_name} → {new_name}")
                success_count += 1
            
        except Exception as e:
            print(f"エラー: {old_name} の変更に失敗 - {e}")
            error_count += 1
    
    print(f"\n=== 変更完了 ===")
    print(f"成功: {success_count} ファイル")
    print(f"エラー: {error_count} ファイル")

def create_backup_list(directory_path, conversions):
    """
    変更履歴をテキストファイルに保存
    """
    try:
        backup_file = os.path.join(directory_path, "filename_conversion_log.txt")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("=== ファイル名変更・画像変換履歴 ===\n\n")
            for conversion in conversions:
                old_name = conversion['old_name']
                new_name = conversion['new_name']
                convert_to_webp = conversion['convert_to_webp']
                
                f.write(f"変更前: {old_name}\n")
                f.write(f"変更後: {new_name}\n")
                
                if convert_to_webp:
                    f.write("画像変換: WebPに変換\n")
                    
                f.write("-" * 50 + "\n")
        
        print(f"変更履歴を保存しました: {backup_file}")
    
    except Exception as e:
        print(f"履歴保存エラー: {e}")

def check_pillow_installation():
    """
    Pillowがインストールされているかチェック
    """
    try:
        from PIL import Image
        return True
    except ImportError:
        print("Error: Pillowがインストールされていません。")
        print("以下のコマンドでインストールしてください:")
        print("pip install Pillow")
        return False

def main():
    """
    メイン処理
    """
    directory_path = '.'
    
    print("日本語ファイル名変換ツール（WebP変換機能付き）")
    print("=" * 50)
    
    # Pillowのチェック
    if not check_pillow_installation():
        return
    
    # 変換対象ファイルを検索
    target_files = find_target_files(directory_path)
    
    if not target_files:
        print("変換対象のファイルが見つかりませんでした。")
        return
    
    print(f"変換対象: {len(target_files)} ファイル\n")
    
    # 画像ファイルの存在チェック
    image_files = [f for f in target_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
    if image_files:
        print(f"画像ファイル: {len(image_files)} ファイル")
        print("画像ファイル名:", ", ".join(image_files))
        print()
    
    # WebP変換の有効/無効を選択
    enable_webp = False
    if image_files:
        response = input("画像ファイル（JPG/PNG）をWebPに変換しますか？ (y/N): ").strip().lower()
        enable_webp = response in ['y', 'yes', 'はい']
        
        if enable_webp:
            print(f"WebP変換品質: {WEBP_QUALITY}%\n")
    
    # PyKakasiのテスト
    print("=== 変換テスト ===")
    test_text = "銀だこキッチンカー"
    result = converter.do(test_text)
    print(f"テスト: '{test_text}' → '{result}'\n")
    
    # 変換予定を表示
    conversions = preview_conversions(directory_path, target_files, enable_webp)
    
    if not conversions:
        print("変換可能なファイルがありませんでした。")
        return
    
    # 確認を求める
    print(f"\n{len(conversions)} ファイルの名前を変更します。")
    if enable_webp:
        print("画像ファイルはWebP形式に変換されます。")
    response = input("実行しますか？ (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'はい']:
        # 変更履歴を保存
        create_backup_list(directory_path, conversions)
        
        # ファイル名変更・画像変換を実行
        rename_and_convert_files(directory_path, conversions)
        
        print("\n処理完了！")
    else:
        print("キャンセルされました。")

# 実行
if __name__ == "__main__":
    main()