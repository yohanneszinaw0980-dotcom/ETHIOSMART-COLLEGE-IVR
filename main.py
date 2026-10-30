from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import json
from plyer import tts
import threading

DATA_FILE = "ivr_complete_data.json"

class CollegeIVRApp(App):
    def build(self):
        self.title = "Advanced Multilingual IVR System - Admin Dashboard"
        self.load_data()
        
        self.sm = ScreenManager()
        
        # 1. Main User Screen
        self.main_screen = Screen(name='main')
        self.setup_main_screen(self.main_screen)
        self.sm.add_widget(self.main_screen)
        
        # 2. Admin Dashboard Screen
        self.admin_screen = Screen(name='admin')
        self.setup_admin_screen(self.admin_screen)
        self.sm.add_widget(self.admin_screen)
        
        # 3. View VIP Screen
        self.vip_screen = Screen(name='vip_view')
        self.sm.add_widget(self.vip_screen)
        
        # 4. View Main Menus Screen
        self.main_menu_screen = Screen(name='main_menu_view')
        self.sm.add_widget(self.main_menu_screen)

        # 5. View Sub Menus Screen
        self.sub_menu_screen = Screen(name='sub_menu_view')
        self.sm.add_widget(self.sub_menu_screen)

        # 6. View Sub-Sub Menus Screen
        self.sub_sub_menu_screen = Screen(name='sub_sub_menu_view')
        self.sm.add_widget(self.sub_sub_menu_screen)
        
        return self.sm

    def speak(self, text):
        def run_speech():
            try:
                tts.speak(message=text)
            except Exception as e:
                print(f"TTS Error: {e}")
        threading.Thread(target=run_speech, daemon=True).start()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.menu_mapping = data.get('menu_mapping', {})
                    self.vip_list = data.get('vip_list', [])
                    self.system_enabled = data.get('system_enabled', True)
            except:
                self.init_default_data()
        else:
            self.init_default_data()

    def init_default_data(self):
        self.menu_mapping = {
            '1': {
                'name': 'Amharic', 
                'prompt': 'ለአማርኛ 1ን ይጫኑ',
                'sub_menu': {
                    '1': {
                        'name': 'ምዝገባ', 
                        'prompt': 'ለምዝገባ 1ን ይጫኑ',
                        'sub_menu': {
                            '1': {'name': 'ዲግሪ ፕሮግራም', 'prompt': 'ለዲግሪ 1ን ይጫኑ', 'sub_menu': {}},
                            '2': {'name': 'ማስተርስ ፕሮግራም', 'prompt': 'ለማስተርስ 2ን ይጫኑ', 'sub_menu': {}}
                        }
                    },
                    '2': {'name': 'የፈተና ውጤት', 'prompt': 'ለፈተና ውጤት 2ን ይጫኑ', 'sub_menu': {}}
                }
            },
            '2': {
                'name': 'English', 
                'prompt': 'For English, press 2',
                'sub_menu': {
                    '1': {'name': 'Registration', 'prompt': 'For Registration, press 1', 'sub_menu': {}},
                    '2': {'name': 'Exam Result', 'prompt': 'For Exam Result, press 2', 'sub_menu': {}}
                }
            }
        }
        self.vip_list = ['0911111111', '0922222222']
        self.system_enabled = True
        self.save_data()

    def save_data(self):
        data = {
            'menu_mapping': self.menu_mapping,
            'vip_list': self.vip_list,
            'system_enabled': self.system_enabled
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def setup_main_screen(self, screen):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        self.status_label = Label(
            text='Status: Calls Open (Active - Offline)' if self.system_enabled else 'Status: System Disabled (Closed)', 
            font_size='15sp', size_hint=(1, 0.08), 
            color=(0.2, 0.8, 0.2, 1) if self.system_enabled else (0.9, 0.2, 0.2, 1)
        )
        layout.add_widget(self.status_label)
        
        btn_to_admin = Button(text='Open Admin Dashboard', size_hint=(1, 0.09), background_color=(0.5, 0.3, 0.7, 1))
        btn_to_admin.bind(on_press=lambda x: setattr(self.sm, 'current', 'admin'))
        layout.add_widget(btn_to_admin)
        
        caller_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.09))
        self.caller_text_input = TextInput(hint_text='Enter incoming caller number...', multiline=False)
        btn_simulate_call = Button(text='Simulate Call', size_hint=(0.4, 1), background_color=(0.8, 0.6, 0.1, 1))
        btn_simulate_call.bind(on_press=self.simulate_incoming_call)
        caller_layout.add_widget(self.caller_text_input)
        caller_layout.add_widget(btn_simulate_call)
        layout.add_widget(caller_layout)
        
        layout.add_widget(Label(text='Active Main Menu Options:', font_size='13sp', size_hint=(1, 0.04)))
        self.menu_btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.12))
        self.create_menu_buttons()
        layout.add_widget(self.menu_btn_layout)
        
        self.log_output = TextInput(text='[System Initialized]: IVR Ready...\n', readonly=True, font_size='12sp', size_hint=(1, 0.4))
        layout.add_widget(self.log_output)
        
        self.current_caller = None
        self.current_menu_pointer = self.menu_mapping
        screen.add_widget(layout)

    def setup_admin_screen(self, screen):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        layout.add_widget(Label(text='[Admin Dashboard] Menu & VIP Management', font_size='15sp', size_hint=(1, 0.08), color=(0.9, 0.7, 0.2, 1)))
        
        ctrl_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.09))
        self.btn_toggle_sys = Button(
            text='Disable System' if self.system_enabled else 'Enable System',
            background_color=(0.8, 0.3, 0.3, 1) if self.system_enabled else (0.2, 0.7, 0.3, 1),
            size_hint=(0.35, 1)
        )
        self.btn_toggle_sys.bind(on_press=self.toggle_system_status)
        
        self.vip_input = TextInput(hint_text='VIP Number', multiline=False, size_hint=(0.4, 1))
        btn_add_vip = Button(text='Add VIP', background_color=(0.3, 0.6, 0.8, 1), size_hint=(0.25, 1))
        btn_add_vip.bind(on_press=self.add_vip_number)
        
        ctrl_layout.add_widget(self.btn_toggle_sys)
        ctrl_layout.add_widget(self.vip_input)
        ctrl_layout.add_widget(btn_add_vip)
        layout.add_widget(ctrl_layout)

        btn_view_vip = Button(text='View VIP Numbers List', size_hint=(1, 0.09), background_color=(0.2, 0.5, 0.6, 1))
        btn_view_vip.bind(on_press=self.open_vip_view_screen)
        layout.add_widget(btn_view_vip)

        layout.add_widget(Label(text='Path (e.g. 1 for Main, 1.1 for Sub, 1.1.1 for Sub-Sub):', font_size='12sp', size_hint=(1, 0.04)))
        
        input_layout1 = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.09))
        self.adm_path = TextInput(hint_text='Path (e.g. 1 or 1.1)', multiline=False, size_hint=(0.3, 1))
        self.adm_name = TextInput(hint_text='Title / Name', multiline=False, size_hint=(0.7, 1))
        input_layout1.add_widget(self.adm_path)
        input_layout1.add_widget(self.adm_name)
        layout.add_widget(input_layout1)

        input_layout2 = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.09))
        self.adm_prompt = TextInput(hint_text='Voice Prompt Content', multiline=False, size_hint=(1, 1))
        input_layout2.add_widget(self.adm_prompt)
        layout.add_widget(input_layout2)
        
        btn_add_menu = Button(text='Add / Update Menu', size_hint=(1, 0.09), background_color=(0.2, 0.7, 0.5, 1))
        btn_add_menu.bind(on_press=self.admin_add_menu)
        layout.add_widget(btn_add_menu)

        btn_view_main = Button(text='View Main Menu (Edit & Delete)', size_hint=(1, 0.09), background_color=(0.6, 0.4, 0.2, 1))
        btn_view_main.bind(on_press=self.open_main_menu_view_screen)
        layout.add_widget(btn_view_main)
        
        btn_back = Button(text='< Back to Main Page', size_hint=(1, 0.1), background_color=(0.3, 0.5, 0.7, 1))
        btn_back.bind(on_press=lambda x: setattr(self.sm, 'current', 'main'))
        layout.add_widget(btn_back)
        
        screen.add_widget(layout)

    # --- VIP View Screen with Edit & Delete ---
    def open_vip_view_screen(self, instance):
        self.build_vip_view_layout()
        self.sm.current = 'vip_view'

    def build_vip_view_layout(self):
        self.vip_screen.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text='[VIP Management] View, Edit & Delete VIP Numbers', font_size='15sp', size_hint=(1, 0.08), color=(0.9, 0.7, 0.2, 1)))
        
        scroll = ScrollView(size_hint=(1, 0.75))
        v_list_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        v_list_layout.bind(minimum_height=v_list_layout.setter('height'))
        
        if not self.vip_list:
            v_list_layout.add_widget(Label(text='No VIP numbers registered.', font_size='13sp', size_hint_y=None, height=40))
        else:
            for num in list(self.vip_list):
                row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=50)
                row.add_widget(Label(text=num, font_size='14sp', size_hint_x=0.4))
                
                btn_edit = Button(text='Edit', background_color=(0.8, 0.6, 0.1, 1), size_hint_x=0.3)
                btn_edit.bind(on_press=lambda x, n=num: self.load_vip_to_edit(n))
                
                btn_del = Button(text='Delete', background_color=(0.8, 0.3, 0.3, 1), size_hint_x=0.3)
                btn_del.bind(on_press=lambda x, n=num: self.delete_specific_vip(n))
                
                row.add_widget(btn_edit)
                row.add_widget(btn_del)
                
                v_list_layout.add_widget(row)
                
        scroll.add_widget(v_list_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(text='< Back to Admin Dashboard', size_hint=(1, 0.1), background_color=(0.3, 0.5, 0.7, 1))
        btn_back.bind(on_press=lambda x: setattr(self.sm, 'current', 'admin'))
        layout.add_widget(btn_back)
        
        self.vip_screen.add_widget(layout)

    def load_vip_to_edit(self, num):
        if num in self.vip_list:
            self.vip_list.remove(num)
            self.save_data()
            self.vip_input.text = num
            self.sm.current = 'admin'

    def delete_specific_vip(self, num):
        if num in self.vip_list:
            self.vip_list.remove(num)
            self.save_data()
            self.build_vip_view_layout()

    # --- Main Menu View Screen ---
    def open_main_menu_view_screen(self, instance):
        self.build_main_menu_view_layout()
        self.sm.current = 'main_menu_view'

    def build_main_menu_view_layout(self):
        self.main_menu_screen.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text='[Main Menu Manager] View, Edit, Delete & Explore Sub-Menus', font_size='14sp', size_hint=(1, 0.08), color=(0.9, 0.7, 0.2, 1)))
        
        scroll = ScrollView(size_hint=(1, 0.75))
        m_list_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        m_list_layout.bind(minimum_height=m_list_layout.setter('height'))
        
        if not self.menu_mapping:
            m_list_layout.add_widget(Label(text='No Main Menus available.', font_size='13sp', size_hint_y=None, height=40))
        else:
            for key, info in self.menu_mapping.items():
                row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=55)
                row.add_widget(Label(text=f"[{key}] {info.get('name')}", font_size='13sp', size_hint_x=0.4))
                
                btn_sub = Button(text='View Sub', background_color=(0.2, 0.6, 0.8, 1), size_hint_x=0.2)
                btn_sub.bind(on_press=lambda x, k=key: self.open_sub_menu_view_screen(k))
                
                btn_edit = Button(text='Edit', background_color=(0.8, 0.6, 0.1, 1), size_hint_x=0.2)
                btn_edit.bind(on_press=lambda x, k=key, inf=info: self.load_menu_to_edit(k, inf))
                
                btn_del = Button(text='Delete', background_color=(0.8, 0.3, 0.3, 1), size_hint_x=0.2)
                btn_del.bind(on_press=lambda x, k=key: self.delete_main_menu_item(k))
                
                row.add_widget(btn_sub)
                row.add_widget(btn_edit)
                row.add_widget(btn_del)
                m_list_layout.add_widget(row)
                
        scroll.add_widget(m_list_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(text='< Back to Admin Dashboard', size_hint=(1, 0.1), background_color=(0.3, 0.5, 0.7, 1))
        btn_back.bind(on_press=lambda x: setattr(self.sm, 'current', 'admin'))
        layout.add_widget(btn_back)
        
        self.main_menu_screen.add_widget(layout)

    def load_menu_to_edit(self, key, info):
        self.adm_path.text = key
        self.adm_name.text = info.get('name', '')
        self.adm_prompt.text = info.get('prompt', '')
        self.sm.current = 'admin'

    def delete_main_menu_item(self, key):
        if key in self.menu_mapping:
            del self.menu_mapping[key]
            self.save_data()
            self.create_menu_buttons()
            self.build_main_menu_view_layout()

    # --- Sub Menu View Screen ---
    def open_sub_menu_view_screen(self, parent_key):
        self.build_sub_menu_view_layout(parent_key)
        self.sm.current = 'sub_menu_view'

    def build_sub_menu_view_layout(self, parent_key):
        self.sub_menu_screen.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=f'[Sub-Menu Manager] Under Parent [{parent_key}]', font_size='14sp', size_hint=(1, 0.08), color=(0.9, 0.7, 0.2, 1)))
        
        scroll = ScrollView(size_hint=(1, 0.75))
        s_list_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        s_list_layout.bind(minimum_height=s_list_layout.setter('height'))
        
        sub_menus = self.menu_mapping.get(parent_key, {}).get('sub_menu', {})
        if not sub_menus:
            s_list_layout.add_widget(Label(text='No Sub-Menus available.', font_size='13sp', size_hint_y=None, height=40))
        else:
            for key, info in sub_menus.items():
                row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=55)
                row.add_widget(Label(text=f"[{parent_key}.{key}] {info.get('name')}", font_size='13sp', size_hint_x=0.4))
                
                btn_subsub = Button(text='View SubSub', background_color=(0.2, 0.6, 0.8, 1), size_hint_x=0.2)
                btn_subsub.bind(on_press=lambda x, pk=parent_key, sk=key: self.open_sub_sub_menu_view_screen(pk, sk))
                
                btn_edit = Button(text='Edit', background_color=(0.8, 0.6, 0.1, 1), size_hint_x=0.2)
                btn_edit.bind(on_press=lambda x, pk=parent_key, sk=key, inf=info: self.load_sub_menu_to_edit(pk, sk, inf))
                
                btn_del = Button(text='Delete', background_color=(0.8, 0.3, 0.3, 1), size_hint_x=0.2)
                btn_del.bind(on_press=lambda x, pk=parent_key, sk=key: self.delete_sub_menu_item(pk, sk))
                
                row.add_widget(btn_subsub)
                row.add_widget(btn_edit)
                row.add_widget(btn_del)
                s_list_layout.add_widget(row)
                
        scroll.add_widget(s_list_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(text='< Back to Main Menus', size_hint=(1, 0.1), background_color=(0.3, 0.5, 0.7, 1))
        btn_back.bind(on_press=lambda x: setattr(self.sm, 'current', 'main_menu_view'))
        layout.add_widget(btn_back)
        
        self.sub_menu_screen.add_widget(layout)

    def load_sub_menu_to_edit(self, parent_key, sub_key, info):
        self.adm_path.text = f"{parent_key}.{sub_key}"
        self.adm_name.text = info.get('name', '')
        self.adm_prompt.text = info.get('prompt', '')
        self.sm.current = 'admin'

    def delete_sub_menu_item(self, parent_key, sub_key):
        if parent_key in self.menu_mapping and 'sub_menu' in self.menu_mapping[parent_key]:
            if sub_key in self.menu_mapping[parent_key]['sub_menu']:
                del self.menu_mapping[parent_key]['sub_menu'][sub_key]
                self.save_data()
                self.build_sub_menu_view_layout(parent_key)

    # --- Sub-Sub Menu View Screen ---
    def open_sub_sub_menu_view_screen(self, parent_key, sub_key):
        self.build_sub_sub_menu_view_layout(parent_key, sub_key)
        self.sm.current = 'sub_sub_menu_view'

    def build_sub_sub_menu_view_layout(self, parent_key, sub_key):
        self.sub_sub_menu_screen.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=f'[Sub-Sub-Menu Manager] Under [{parent_key}.{sub_key}]', font_size='14sp', size_hint=(1, 0.08), color=(0.9, 0.7, 0.2, 1)))
        
        scroll = ScrollView(size_hint=(1, 0.75))
        ss_list_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        ss_list_layout.bind(minimum_height=ss_list_layout.setter('height'))
        
        sub_sub_menus = self.menu_mapping.get(parent_key, {}).get('sub_menu', {}).get(sub_key, {}).get('sub_menu', {})
        if not sub_sub_menus:
            ss_list_layout.add_widget(Label(text='No Sub-Sub-Menus available.', font_size='13sp', size_hint_y=None, height=40))
        else:
            for key, info in sub_sub_menus.items():
                row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=55)
                row.add_widget(Label(text=f"[{parent_key}.{sub_key}.{key}] {info.get('name')}", font_size='13sp', size_hint_x=0.5))
                
                btn_edit = Button(text='Edit', background_color=(0.8, 0.6, 0.1, 1), size_hint_x=0.25)
                btn_edit.bind(on_press=lambda x, pk=parent_key, sk=sub_key, ssk=key, inf=info: self.load_sub_sub_menu_to_edit(pk, sk, ssk, inf))
                
                btn_del = Button(text='Delete', background_color=(0.8, 0.3, 0.3, 1), size_hint_x=0.25)
                btn_del.bind(on_press=lambda x, pk=parent_key, sk=sub_key, ssk=key: self.delete_sub_sub_menu_item(pk, sk, ssk))
                
                row.add_widget(btn_edit)
                row.add_widget(btn_del)
                ss_list_layout.add_widget(row)
                
        scroll.add_widget(ss_list_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(text='< Back to Sub Menus', size_hint=(1, 0.1), background_color=(0.3, 0.5, 0.7, 1))
        btn_back.bind(on_press=lambda x: self.open_sub_menu_view_screen(parent_key))
        layout.add_widget(btn_back)
        
        self.sub_sub_menu_screen.add_widget(layout)

    def load_sub_sub_menu_to_edit(self, parent_key, sub_key, sub_sub_key, info):
        self.adm_path.text = f"{parent_key}.{sub_key}.{sub_sub_key}"
        self.adm_name.text = info.get('name', '')
        self.adm_prompt.text = info.get('prompt', '')
        self.sm.current = 'admin'

    def delete_sub_sub_menu_item(self, parent_key, sub_key, sub_sub_key):
        try:
            sub_sub_dict = self.menu_mapping[parent_key]['sub_menu'][sub_key]['sub_menu']
            if sub_sub_key in sub_sub_dict:
                del sub_sub_dict[sub_sub_key]
                self.save_data()
                self.build_sub_sub_menu_view_layout(parent_key, sub_key)
        except Exception as e:
            print(f"Delete Error: {e}")

    # --- Standard Admin Actions ---
    def toggle_system_status(self, instance):
        self.system_enabled = not self.system_enabled
        self.save_data()
        if self.system_enabled:
            self.btn_toggle_sys.text = 'Disable System'
            self.btn_toggle_sys.background_color = (0.8, 0.3, 0.3, 1)
            self.status_label.text = 'Status: Calls Open (Active - Offline)'
            self.status_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.btn_toggle_sys.text = 'Enable System'
            self.btn_toggle_sys.background_color = (0.2, 0.7, 0.3, 1)
            self.status_label.text = 'Status: System Disabled (Closed)'
            self.status_label.color = (0.9, 0.2, 0.2, 1)

    def add_vip_number(self, instance):
        num = self.vip_input.text.strip()
        if num and num not in self.vip_list:
            self.vip_list.append(num)
            self.save_data()
            self.vip_input.text = ''

    def create_menu_buttons(self):
        self.menu_btn_layout.clear_widgets()
        for digit, info in self.menu_mapping.items():
            btn = Button(
                text=f"Press {digit}\n({info.get('name', 'Menu')})",
                font_size='11sp',
                background_color=(0.3, 0.5, 0.7, 1)
            )
            btn.bind(on_press=lambda x, d=digit: self.simulate_keypress(d))
            self.menu_btn_layout.add_widget(btn)

    def admin_add_menu(self, instance):
        path_input = self.adm_path.text.strip()
        name = self.adm_name.text.strip()
        prompt = self.adm_prompt.text.strip()
        
        if not path_input or not name or not prompt:
            return

        parts = path_input.split('.')
        current = self.menu_mapping
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {'name': 'New Menu', 'prompt': '', 'sub_menu': {}}
            if 'sub_menu' not in current[part]:
                current[part]['sub_menu'] = {}
            current = current[part]['sub_menu']
        
        final_key = parts[-1]
        if final_key not in current:
            current[final_key] = {'name': name, 'prompt': prompt, 'sub_menu': {}}
        else:
            current[final_key]['name'] = name
            current[final_key]['prompt'] = prompt

        self.save_data()
        self.create_menu_buttons()
        
        self.adm_path.text = ''
        self.adm_name.text = ''
        self.adm_prompt.text = ''

    def simulate_incoming_call(self, instance):
        if not self.system_enabled:
            self.log_output.text += "-> [Call Blocked]: System is disabled by Admin.\n"
            self.speak("ይቅርታ፣ ሲስተሙ በአሁኑ ሰዓት ዝግ ነው።")
            return

        caller_number = self.caller_text_input.text.strip()
        if not caller_number:
            return
        
        self.current_caller = caller_number
        self.current_menu_pointer = self.menu_mapping
        
        if caller_number in self.vip_list:
            speech_text = "እንኳን ደህና መጡ ክቡር/ክብርት ቪአይፒ ተጠቃሚ። " + "፣ ".join([info['prompt'] for info in self.menu_mapping.values() if info.get('prompt')]) + "።"
            self.log_output.text += f"\n-> [VIP Call]: From {caller_number}\n-> [Voice AI]: {speech_text}\n"
        else:
            speech_text = "እንኳን ደህና መጡ። " + "፣ ".join([info['prompt'] for info in self.menu_mapping.values() if info.get('prompt')]) + "።"
            self.log_output.text += f"\n-> [Call]: From {caller_number}\n-> [Voice AI]: {speech_text}\n"
            
        self.speak(speech_text)
        self.caller_text_input.text = ''

    def simulate_keypress(self, digit):
        if not self.current_caller:
            self.log_output.text += "-> [Error]: Simulate a call first.\n"
            return
        
        if digit in self.current_menu_pointer:
            selected_item = self.current_menu_pointer[digit]
            sub_menus = selected_item.get('sub_menu', {})
            
            if sub_menus:
                self.current_menu_pointer = sub_menus
                sub_prompts = [item['prompt'] for item in sub_menus.values() if item.get('prompt')]
                speech_text = f"{selected_item['name']} ተመርጧል። " + "፣ ".join(sub_prompts) + "።"
                self.log_output.text += f"-> [Input: {digit}] -> {selected_item['name']}\n-> [Prompt]: {speech_text}\n"
                self.speak(speech_text)
            else:
                speech_text = f"{selected_item['name']} አገልግሎት ተመርጧል። እናመሰግናለን።"
                self.log_output.text += f"-> [Final Input: {digit}] -> {selected_item['name']} Selected. Call Ending.\n"
                self.speak(speech_text)
                self.current_menu_pointer = self.menu_mapping
                self.current_caller = None
        else:
            self.log_output.text += f"-> [Input: {digit}] -> Invalid option.\n"
            self.speak("ልክ ያልሆነ ቁጥር መርጠዋል እባክዎ እንደገና ይሞክሩ።")

if __name__ == '__main__':
    CollegeIVRApp().run()
