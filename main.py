import re
import math
import random
import hashlib
import urllib.request
import json
import sys
import traceback
from io import StringIO

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

def call_gemini_ai(prompt):
    return f"[AI Response] คุณถามว่า: {prompt}"

KEYWORDS = [
    (r'ถ้า\s+(.+?)\s+และ\s+(.+?):', r'if \1 and \2:'),
    (r'ถ้า\s+(.+?)\s+หรือ\s+(.+?):', r'if \1 or \2:'),
    (r'ถ้า\s+(.+?):', r'if \1:'),
    (r'เผื่อว่า\s+(.+?):', r'elif \1:'),
    (r'มิฉะนั้น:', r'else:'),
    (r'ตราบใดที่\s+(.+?):', r'while \1:'),
    (r'สำหรับ\s+(\w+)\s+ใน\s+(.+?):', r'for \1 in \2:'),
    (r'หยุด:', r'break'),
    (r'ข้าม:', r'continue'),
    (r'สร้างฟังก์ชัน\s+(\w+)\((.+?)\):', r'def \1(\2):'),
    (r'คืนค่า\s+(.+)', r'return \1'),
    (r'ลองทำ:', r'try:'),
    (r'จับข้อผิดพลาด:', r'except:'),
    (r'นำเข้าโมดูล\s+(\w+)', r'import \1'),
    (r'รากที่สองของ\((.+?)\)', r'math.sqrt(\1)'),
    (r'สุ่มเลขจาก\((.+?)\s*ถึง\s*(.+?)\)', r'random.randint(\1, \2)'),
    (r'เข้ารหัส\s+SHA256\((.+?)\)', r'hashlib.sha256(str(\1).encode("utf-8")).hexdigest()'),
    (r'โหลดข้อมูลจากเว็บ\("(.+?)"\)', r'json.loads(urllib.request.urlopen("\1", timeout=10).read().decode("utf-8"))'),
    (r'ถามปัญญาประดิษฐ์\((.+?)\)', r'call_gemini_ai(\1)'),
    (r'แสดงผล\((.+?)\)', r'print(\1)'),
    (r'ให้\s+(\w+)\s*=\s*(.+)', r'\1 = \2'),
]

def translate_to_python(thai_code):
    py_lines = []
    for line in thai_code.splitlines():
        indent = line[:-len(line.lstrip())] if line.lstrip() else ""
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            py_lines.append(line)
            continue
        translated = stripped
        changed = True
        max_iterations = 20
        iteration = 0
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            for pattern, replacement in KEYWORDS:
                new_translated = re.sub(pattern, replacement, translated)
                if new_translated != translated:
                    translated = new_translated
                    changed = True
        py_lines.append(indent + translated)
    return '\n'.join(py_lines)

class ThaiLangApp(App):
    def build(self):
        self.title = "ThaiLang Compiler"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.code_input = TextInput(
            hint_text='พิมพ์โค้ดภาษาไทยที่นี่...\nเช่น:\nให้ ข้อความ = "สวัสดีชาวไทย"\nให้ รหัส = เข้ารหัส SHA256(ข้อความ)\nแสดงผล(รหัส)',
            multiline=True, font_size=16, size_hint_y=0.5
        )
        layout.add_widget(self.code_input)
        run_btn = Button(text='🚀 รันโปรแกรมภาษาไทย', size_hint_y=None, height=50, font_size=18, background_color=(0.1, 0.6, 0.3, 1))
        run_btn.bind(on_press=self.run_code)
        layout.add_widget(run_btn)
        self.output_label = Label(text='[ผลลัพธ์การทำงานจะแสดงที่นี่]', font_size=16, halign='left', valign='top', size_hint_y=None)
        self.output_label.bind(width=lambda *x: setattr(self.output_label, 'text_size', (self.output_label.width, None)))
        self.output_label.bind(texture_size=lambda *x: setattr(self.output_label, 'height', self.output_label.texture_size[1]))
        scroll = ScrollView(size_hint=(1, 0.4))
        scroll.add_widget(self.output_label)
        layout.add_widget(scroll)
        return layout

    def run_code(self, instance):
        thai_code = self.code_input.text
        if not thai_code.strip():
            self.output_label.text = "❌ กรุณาพิมพ์โค้ดภาษาไทยก่อนรัน"
            return
        try:
            py_code = translate_to_python(thai_code)
            old_stdout = sys.stdout
            new_stdout = StringIO()
            sys.stdout = new_stdout
            try:
                exec_globals = {'call_gemini_ai': call_gemini_ai, '__builtins__': __builtins__}
                exec(py_code, exec_globals)
            finally:
                sys.stdout = old_stdout
            output = new_stdout.getvalue()
            self.output_label.text = output if output else "✅ ทำงานสำเร็จ (ไม่มีการแสดงผล)"
        except Exception:
            self.output_label.text = "❌ เกิดข้อผิดพลาด:\n" + traceback.format_exc()

if __name__ == '__main__':
    ThaiLangApp().run()
1
