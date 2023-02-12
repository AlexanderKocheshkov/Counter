from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.uix.textinput import TextInput
import sqlite3
import os

#Разрешение на создание, хранение файлов
if platform == "android":
	from android.permissions import request_permissions, Permission
	request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

#Если списка кнопок нет, то создаём таблицу для них
if os.path.exists('btn_list.db') == False:
	connection = sqlite3.connect("btn_list.db")
	cursor = connection.cursor()
	sql_create_database = """CREATE TABLE IF NOT exists buttons(
	btnname TEXT PRIMARY KEY,
	btnnum INT);
	"""
	cursor.execute(sql_create_database)
	connection.commit()
	cursor.close()
	connection.close()


class MainScreen(Screen):#Главный (основной) экран
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		boxlayout_main_menu = BoxLayout(orientation = "vertical")
		btn_btns_list = Button(text = "Кнопки!", 
									background_color = ("8cadd3"))
		btn_btns_list.bind(on_press = self.on_press_Lizka_lists)
		btn_crt_nbtn = Button(text = "Новая кнопка!", 
									background_color = ("8cadd3"))
		btn_crt_nbtn.bind(on_press = self.on_press_create_new_button)
		boxlayout_main_menu.add_widget(btn_btns_list)
		boxlayout_main_menu.add_widget(btn_crt_nbtn)
		self.add_widget(boxlayout_main_menu)

	def on_press_Lizka_lists(self, instance): #Переход к списку кнопок-счётчиков
		self.manager.transition.direction = 'left'
		self.manager.current = 'button_list_screen'
    
	def on_press_create_new_button(self, instance): #Переход к созданию новой кнопки-счётчика
		self.manager.transition.direction = 'left'
		self.manager.current = 'button_creation_screen'

class ButtonCreationScreen(Screen): #Экран создания кнопки
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		boxlayout_button_creation = BoxLayout(orientation = "vertical")
		self.t = TextInput(font_size = 30, 
					size_hint_y = None, 
					height = 100) 
		f = Button(text ="Именно так!", 
					font_size ="20sp", 
					background_color = ("8cadd3"))
		f.bind(on_press = self.cr_new_btn)
		boxlayout_button_creation.add_widget(self.t) 
		boxlayout_button_creation.add_widget(f)
		self.add_widget(boxlayout_button_creation)

	def cr_new_btn(self, instance): #Создание кнопки
		new_btn = self.t.text
		connection = sqlite3.connect("btn_list.db")
		cursor = connection.cursor()
		sql_add_new_btn = """INSERT INTO buttons VALUES(?, ?)"""
		cursor.execute(sql_add_new_btn, (self.t.text, 0))
		connection.commit()
		cursor.close()
		connection.close()
		self.manager.transition.direction = 'right'
		self.manager.current = 'main_screen'

class ButtonListScreen(Screen): #Экран со списком существующих кнопок-счётчиков
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		boxlayout_button_list = BoxLayout(orientation = "vertical")
		connection = sqlite3.connect("btn_list.db")
		cursor = connection.cursor()
		get_btns_name = """SELECT * FROM buttons"""
		cursor.execute(get_btns_name)
		btns_name_n_num = cursor.fetchall()
		btns_names = []
		for btn_name, btn_nums in btns_name_n_num:
			btns_names.append(btn_name)
		cursor.close()
		connection.close()
		bx_for_btns = BoxLayout(orientation = "vertical")
		if btns_names != []:
			for btn in btns_names:
				button_from_list = Button(text = btn, 
											background_color = ("8cadd3"))
				button_from_list.bind(on_press = self.open_button)
				bx_for_btns.add_widget(button_from_list)
		else:
			return_to_create = Button(text = "Надо бы создать!", 
											background_color = ("8cadd3"))
			return_to_create.bind(on_press = self.need_to_create)
			bx_for_btns.add_widget(return_to_create)
		boxlayout_button_list.add_widget(bx_for_btns)
		self.add_widget(boxlayout_button_list)

	def open_button(self, instance): #Переход к выбранной кнопке-счётчику
		global x #Ещё не разобрался, как в kivy передать значение на другой экран
		x = instance.text
		self.manager.transition.direction = 'right'
		self.manager.current = 'button_clicker_screen'

	def need_to_create(self, instance): #Если кнопок нет, то переводит на главный экран
		self.manager.transition.direction = 'right'
		self.manager.current = 'main_screen'

class ButtonClickerScreen(Screen): #Экран с кнопкой-счётчик и отображением счёта
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		main_layout = BoxLayout(orientation="vertical")
		self.label = Label(text = "", size_hint = (.7, .9), 
								pos_hint = {'center_x': 0.5, 'center_y': 0.7})
		btn_clicker = Button(text = 'Опять!!!', 
								background_color = ("8cadd3"))
		btn_clicker.bind(on_press=self.on_press_Lizka_button)
		btn_list = Button(text = 'Списки')
		main_layout.add_widget(self.label)
		main_layout.add_widget(btn_clicker)
		self.add_widget(main_layout)


	def on_press_Lizka_button(self, instance): #+1 на счётчик
		connection = sqlite3.connect("btn_list.db")
		cursor = connection.cursor()
		get_btn_num = """SELECT btnnum FROM buttons WHERE btnname = ?"""
		cursor.execute(get_btn_num, (x, ))
		data = cursor.fetchone()
		self.num = data[0]
		self.num += 1
		self.label.text = "Уже " + str(self.num) + "!"
		push_in = """UPDATE buttons SET btnnum = ? WHERE btnname = ?"""
		cursor.execute(push_in, (self.num, x))
		connection.commit()
		cursor.close()
		connection.close()

class MainApp(App):
	def build(self):
		sm = ScreenManager()
		sm.add_widget(MainScreen(name = "main_screen"))
		sm.add_widget(ButtonListScreen(name = "button_list_screen"))
		sm.add_widget(ButtonClickerScreen(name = "button_clicker_screen"))
		sm.add_widget(ButtonCreationScreen(name = "button_creation_screen"))
		return sm

if __name__ == '__main__':
	app = MainApp()
	app.run()
