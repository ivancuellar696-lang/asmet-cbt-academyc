"""
ASMET CBT ACADEMYC v5.0 - Plataforma de Matemáticas Adaptativa
Sistema especializado en Competencias Basadas en Tareas (CBT)
"""

import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar

# Y también mantener algunas de Kivy normal
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
import random
import json
import os
from datetime import datetime
import sqlite3

# Configuración de ventana
Window.size = (400, 700)
Window.minimum_width, Window.minimum_height = 360, 600

class CBTMathDatabase:
    """Base de datos para seguimiento de progreso CBT"""
    
    def __init__(self):
        self.conn = sqlite3.connect('asmet_cbt_academyc.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Tabla de estudiantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                grade TEXT,
                level TEXT DEFAULT 'basic',
                progress REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de progreso por competencia
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competence_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                competence_code TEXT,
                topic TEXT,
                subtopic TEXT,
                score REAL DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                last_practice TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        ''')
        
        # Tabla de ejercicios CBT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cbt_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competence_code TEXT,
                level TEXT,
                topic TEXT,
                question TEXT,
                answer TEXT,
                options TEXT,
                difficulty TEXT,
                time_limit INTEGER
            )
        ''')
        
        self.conn.commit()
        self.initialize_exercises()
    
    def initialize_exercises(self):
        """Inicializar ejercicios CBT para todos los niveles"""
        cursor = self.conn.cursor()
        
        # Ejercicios para Nivel Básico
        basic_exercises = [
            # Aritmética fundamental
            ('CBT-ARIT-001', 'basic', 'Aritmética', 
             'Calcula: 25 + 37 = ?', '62', '["58", "62", "67", "52"]', 'easy', 60),
            ('CBT-ARIT-002', 'basic', 'Aritmética',
             '¿Cuál es el MCD de 12 y 18?', '6', '["3", "6", "12", "18"]', 'medium', 90),
            # Geometría elemental
            ('CBT-GEO-001', 'basic', 'Geometría',
             'Calcula el perímetro de un cuadrado de lado 5cm', '20', '["15", "20", "25", "10"]', 'easy', 60),
            ('CBT-GEO-002', 'basic', 'Geometría',
             'Área de un triángulo con base 8cm y altura 6cm', '24', '["14", "24", "48", "32"]', 'medium', 90),
            # Álgebra básica
            ('CBT-ALG-001', 'basic', 'Álgebra',
             'Resuelve: 3x + 5 = 17', '4', '["3", "4", "5", "6"]', 'medium', 120),
        ]
        
        for exercise in basic_exercises:
            cursor.execute('''
                INSERT OR IGNORE INTO cbt_exercises 
                (competence_code, level, topic, question, answer, options, difficulty, time_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', exercise)
        
        self.conn.commit()

class CBTLearningSystem:
    """Sistema de aprendizaje basado en Competencias CBT"""
    
    def __init__(self):
        self.levels = {
            'basic': self.get_basic_competences(),
            'medium': self.get_medium_competences(),
            'high': self.get_high_competences(),
            'advanced': self.get_advanced_competences()
        }
    
    def get_basic_competences(self):
        """Competencias CBT para Nivel Básico"""
        return {
            'Aritmética Fundamental': {
                'code': 'CBT-ARIT-BAS',
                'subtopics': [
                    'Operaciones básicas (+, -, ×, ÷) con números naturales',
                    'Fracciones y decimales básicos',
                    'Mínimo común múltiplo y máximo común divisor',
                    'Porcentajes y proporciones simples'
                ],
                'color': [0.2, 0.6, 0.9, 1],
                'description': 'Desarrolla competencias básicas de cálculo numérico'
            },
            'Geometría Elemental': {
                'code': 'CBT-GEO-BAS',
                'subtopics': [
                    'Figuras planas: triángulo, cuadrado, rectángulo, círculo',
                    'Perímetro y área de figuras simples',
                    'Ángulos: tipos y medición',
                    'Unidades de medida básicas'
                ],
                'color': [0.3, 0.8, 0.5, 1],
                'description': 'Comprensión de formas y medidas básicas'
            },
            'Introducción al Álgebra': {
                'code': 'CBT-ALG-BAS',
                'subtopics': [
                    'Expresiones algebraicas simples',
                    'Ecuaciones de primer grado con una incógnita',
                    'Unidades de medida (longitud, masa, capacidad, tiempo)',
                    'Problemas de aplicación básicos'
                ],
                'color': [0.9, 0.6, 0.2, 1],
                'description': 'Fundamentos del pensamiento algebraico'
            }
        }
    
    def get_medium_competences(self):
        """Competencias CBT para Nivel Medio"""
        return {
            'Álgebra Intermedia': {
                'code': 'CBT-ALG-MED',
                'subtopics': [
                    'Ecuaciones de primer grado con dos incógnitas',
                    'Sistemas de ecuaciones lineales (métodos de solución)',
                    'Polinomios: operaciones y factorización básica',
                    'Ecuaciones de segundo grado (fórmula general)'
                ],
                'color': [0.8, 0.3, 0.6, 1],
                'description': 'Competencias en resolución de sistemas algebraicos'
            },
            'Geometría Intermedia': {
                'code': 'CBT-GEO-MED',
                'subtopics': [
                    'Teorema de Pitágoras',
                    'Semejanza y congruencia de triángulos',
                    'Área y volumen de prismas, pirámides, cilindros, conos',
                    'Transformaciones geométricas (traslación, rotación, reflexión)'
                ],
                'color': [0.4, 0.7, 0.8, 1],
                'description': 'Geometría aplicada a situaciones reales'
            },
            'Estadística Descriptiva': {
                'code': 'CBT-EST-MED',
                'subtopics': [
                    'Media, mediana, moda',
                    'Gráficas de barras, circulares, histogramas',
                    'Probabilidad básica: espacio muestral y eventos',
                    'Cálculo de probabilidades simples'
                ],
                'color': [0.9, 0.4, 0.3, 1],
                'description': 'Competencias en análisis de datos básicos'
            }
        }
    
    def get_high_competences(self):
        """Competencias CBT para Nivel Medio Superior"""
        return {
            'Funciones y Gráficas': {
                'code': 'CBT-FUN-ALT',
                'subtopics': [
                    'Funciones lineales, cuadráticas, exponenciales y logarítmicas',
                    'Dominio y rango',
                    'Transformaciones de funciones',
                    'Aplicaciones de funciones'
                ],
                'color': [0.6, 0.2, 0.8, 1],
                'description': 'Comprensión profunda del concepto de función'
            },
            'Trigonometría': {
                'code': 'CBT-TRI-ALT',
                'subtopics': [
                    'Razones trigonométricas (sen, cos, tan)',
                    'Ley de senos y ley de cosenos',
                    'Identidades trigonométricas fundamentales',
                    'Resolución de triángulos'
                ],
                'color': [0.2, 0.8, 0.7, 1],
                'description': 'Competencias en medición y cálculo angular'
            },
            'Geometría Analítica': {
                'code': 'CBT-GEO-ALT',
                'subtopics': [
                    'Recta: ecuaciones y propiedades',
                    'Circunferencia, parábola, elipse, hipérbola',
                    'Sistemas de coordenadas',
                    'Aplicaciones geométrico-analíticas'
                ],
                'color': [0.8, 0.7, 0.2, 1],
                'description': 'Unión de álgebra y geometría'
            },
            'Cálculo Diferencial': {
                'code': 'CBT-CAL-ALT',
                'subtopics': [
                    'Límites y continuidad',
                    'Derivadas: reglas básicas, máximos y mínimos',
                    'Aplicaciones de la derivada',
                    'Optimización de funciones'
                ],
                'color': [0.9, 0.3, 0.4, 1],
                'description': 'Competencias en análisis de cambio'
            }
        }
    
    def get_advanced_competences(self):
        """Competencias CBT para Nivel Avanzado"""
        return {
            'Cálculo Integral': {
                'code': 'CBT-CAL-AVA',
                'subtopics': [
                    'Técnicas de integración',
                    'Aplicaciones (áreas, volúmenes, longitud de arco)',
                    'Integrales impropias y series',
                    'Aplicaciones físicas y económicas'
                ],
                'color': [0.3, 0.4, 0.9, 1],
                'description': 'Competencias en cálculo de acumulación'
            },
            'Álgebra Lineal': {
                'code': 'CBT-ALG-AVA',
                'subtopics': [
                    'Vectores y matrices',
                    'Espacios vectoriales, bases y dimensión',
                    'Valores y vectores propios',
                    'Transformaciones lineales'
                ],
                'color': [0.7, 0.2, 0.9, 1],
                'description': 'Competencias en estructuras algebraicas lineales'
            },
            'Ecuaciones Diferenciales': {
                'code': 'CBT-EDO-AVA',
                'subtopics': [
                    'EDO de primer y segundo orden',
                    'Sistemas de ecuaciones diferenciales',
                    'Transformada de Laplace',
                    'Aplicaciones en ingeniería y física'
                ],
                'color': [0.2, 0.9, 0.5, 1],
                'description': 'Competencias en modelado dinámico'
            },
            'Matemáticas Discretas': {
                'code': 'CBT-DIS-AVA',
                'subtopics': [
                    'Lógica matemática y teoría de conjuntos avanzada',
                    'Relaciones y funciones',
                    'Teoría de grafos y combinatoria avanzada',
                    'Aplicaciones en ciencias de la computación'
                ],
                'color': [0.9, 0.5, 0.2, 1],
                'description': 'Competencias en matemáticas computacionales'
            },
            'Áreas Especializadas': {
                'code': 'CBT-ESP-AVA',
                'subtopics': [
                    'Topología',
                    'Análisis funcional',
                    'Teoría de números',
                    'Geometría diferencial',
                    'Investigación de operaciones',
                    'Teoría de probabilidad avanzada'
                ],
                'color': [0.4, 0.9, 0.8, 1],
                'description': 'Competencias en áreas de especialización STEM'
            }
        }

class WelcomeScreen(Screen):
    """Pantalla de bienvenida con diseño moderno"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0.13, 0.59, 0.95, 1]
        
        layout = FloatLayout()
        
        # Fondo decorativo
        with layout.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=layout.pos, size=layout.size)
        
        # Logo principal
        logo_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
            spacing=10
        )
        
        logo_symbol = Label(
            text='∑',
            font_size=64,
            color=[1, 1, 1, 1],
            bold=True
        )
        
        logo_text = Label(
            text='ASMET CBT ACADEMYC',
            font_size=32,
            color=[1, 1, 1, 1],
            bold=True
        )
        
        logo_subtitle = Label(
            text='MATEMÁTICAS ADAPTATIVAS',
            font_size=16,
            color=[0.9, 0.9, 0.9, 1]
        )
        
        logo_layout.add_widget(logo_symbol)
        logo_layout.add_widget(logo_text)
        logo_layout.add_widget(logo_subtitle)
        
        # Eslogan
        slogan = Label(
            text='Domina las matemáticas, sin complicaciones',
            font_size=20,
            color=[1, 1, 1, 0.9],
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        slogan.bind(size=slogan.setter('text_size'))
        
        # Descripción
        description = Label(
            text='Transformamos el aprendizaje matemático mediante un sistema especializado en Competencias Basadas en Tareas, ofreciendo seguimiento personalizado y herramientas adaptativas para el éxito académico garantizado.',
            font_size=14,
            color=[1, 1, 1, 0.8],
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            size_hint=(0.8, 0.3)
        )
        description.bind(size=description.setter('text_size'))
        
        # Botones de acción
        buttons_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            spacing=15
        )
        
        start_button = MDRaisedButton(
            text="COMENZAR",
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            md_bg_color=(0.2, 0.6, 0.9, 1),
            text_color=(1, 1, 1, 1),
            font_size='20sp',
            font_name='assets/fonts/Roboto-Bold.ttf',
            bold=True,
            radius=[25]

        )
        start_button.bind(on_press=self.start_learning)
        
        features_button = Button(
            text='VER CARACTERÍSTICAS',
            size_hint_y=0.5,
            background_color=[0.2, 0.6, 0.9, 0.8],
            color=[1, 1, 1, 1],
            font_size=16,
            border_radius=20
        )
        features_button.bind(on_press=self.show_features)
        
        buttons_layout.add_widget(start_button)
        buttons_layout.add_widget(features_button)
        
        layout.add_widget(logo_layout)
        layout.add_widget(slogan)
        layout.add_widget(description)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)
    
    def start_learning(self, instance):
        self.manager.current = 'student_registration'
    
    def show_features(self, instance):
        self.manager.current = 'features'

class StudentRegistrationScreen(Screen):
    """Pantalla de registro de estudiante"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        # Título
        title = Label(
            text='REGISTRO DE ESTUDIANTE',
            font_size=28,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            size_hint_y=0.2
        )
        
        # Formulario
        form_scroll = ScrollView()
        form_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=20,
            padding=20
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Campos del formulario
        self.name_input = self.create_input_field('Nombre completo')
        self.age_input = self.create_input_field('Edad', input_type='number')
        self.grade_input = self.create_input_field('Grado académico')
        
        # Nivel académico
        level_label = Label(
            text='Selecciona tu nivel académico:',
            font_size=16,
            color=[0.4, 0.4, 0.4, 1],
            size_hint_y=None,
            height=40
        )
        
        levels_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        
        levels = [
            ('🏫 Básico', 'Primaria - Inicio Secundaria', 'basic'),
            ('🎓 Medio', 'Secundaria', 'medium'),
            ('📚 Medio Superior', 'Preparatoria/Bachillerato', 'high'),
            ('🎯 Avanzado', 'Universidad - STEM', 'advanced')
        ]
        
        self.selected_level = 'basic'
        self.level_buttons = {}
        
        for icon, desc, level in levels:
            level_btn = Button(
                text=f'{icon}\n{desc}',
                font_size=12,
                background_color=[0.2, 0.6, 0.9, 0.3] if level == 'basic' else [0.9, 0.9, 0.9, 1],
                color=[0.2, 0.2, 0.2, 1],
                border_radius=15,
                halign='center',
                valign='middle'
            )
            level_btn.bind(on_press=lambda x, lvl=level: self.select_level(lvl))
            self.level_buttons[level] = level_btn
            levels_grid.add_widget(level_btn)
        
        form_layout.add_widget(level_label)
        form_layout.add_widget(levels_grid)
        form_layout.add_widget(self.name_input)
        form_layout.add_widget(self.age_input)
        form_layout.add_widget(self.grade_input)
        
        form_scroll.add_widget(form_layout)
        
        # Botones
        buttons_layout = BoxLayout(size_hint_y=0.2, spacing=20)
        
        back_btn = Button(
            text='← Volver',
            background_color=[0.8, 0.8, 0.8, 1],
            color=[0.2, 0.2, 0.2, 1]
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        
        register_btn = Button(
            text='REGISTRARSE Y COMENZAR',
            background_color=[0.2, 0.8, 0.4, 1],
            color=[1, 1, 1, 1],
            font_size=16,
            bold=True
        )
        register_btn.bind(on_press=self.register_student)
        
        buttons_layout.add_widget(back_btn)
        buttons_layout.add_widget(register_btn)
        
        layout.add_widget(title)
        layout.add_widget(form_scroll)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)
    
    def create_input_field(self, hint_text, input_type='text'):
        """Crea un campo de entrada estilizado"""
        field = BoxLayout(orientation='vertical', size_hint_y=None, height=70, spacing=5)
        
        label = Label(
            text=hint_text,
            font_size=14,
            color=[0.4, 0.4, 0.4, 1],
            halign='left',
            size_hint_y=0.4
        )
        
        if input_type == 'number':
            input_field = TextInput(
                hint_text=hint_text,
                multiline=False,
                font_size=16,
                input_type='number'
            )
        else:
            input_field = TextInput(
                hint_text=hint_text,
                multiline=False,
                font_size=16
            )
        
        field.add_widget(label)
        field.add_widget(input_field)
        return field
    
    def select_level(self, level):
        """Selecciona el nivel académico"""
        self.selected_level = level
        for lvl, btn in self.level_buttons.items():
            btn.background_color = [0.2, 0.6, 0.9, 0.3] if lvl == level else [0.9, 0.9, 0.9, 1]
    
    def register_student(self, instance):
        """Registra al estudiante"""
        name = self.name_input.children[0].text.strip()
        age = self.age_input.children[0].text.strip()
        grade = self.grade_input.children[0].text.strip()
        
        if not name:
            self.show_message('Por favor ingresa tu nombre', 'error')
            return
        
        # Guardar datos del estudiante en la app
        app = App.get_running_app()
        app.student_data = {
            'name': name,
            'age': age,
            'grade': grade,
            'level': self.selected_level
        }
        
        self.show_message(f'¡Bienvenido {name}!', 'success')
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 1.5)
    
    def show_message(self, message, msg_type):
        """Muestra un mensaje emergente"""
        colors = {
            'success': [0.2, 0.8, 0.4, 1],
            'error': [0.9, 0.3, 0.3, 1],
            'warning': [0.96, 0.77, 0.23, 1]
        }
        
        popup = ModalView(size_hint=(0.8, 0.2), background_color=[0, 0, 0, 0])
        content = BoxLayout(orientation='vertical', padding=20)
        
        with content.canvas.before:
            Color(*colors.get(msg_type, [0.2, 0.6, 0.9, 1]))
            RoundedRectangle(pos=content.pos, size=content.size, radius=[15])
        
        content.add_widget(Label(
            text=message,
            font_size=16,
            color=[1, 1, 1, 1],
            halign='center'
        ))
        
        popup.add_widget(content)
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

class FeaturesScreen(Screen):
    """Pantalla de características de la plataforma"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            font_size=24,
            background_color=[0.8, 0.8, 0.8, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'welcome')
        )
        
        title = Label(
            text='¿QUÉ HACE ASMET CBT ACADEMYC?',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # Contenido
        scroll = ScrollView()
        features_container = BoxLayout(
            orientation='vertical',
            spacing=25,
            size_hint_y=None,
            padding=20
        )
        features_container.bind(minimum_height=features_container.setter('height'))
        
        # Características
        features = [
            ('📊', 'DIAGNOSTICA', 'Identifica el nivel actual y las brechas de conocimiento mediante evaluaciones adaptativas basadas en Competencias Basadas en Tareas.'),
            ('🎯', 'PERSONALIZA', 'Diseña rutas de aprendizaje únicas para cada estudiante, focalizándose en sus áreas de mejora específicas.'),
            ('📚', 'ENSEÑA', 'Proporciona contenido especializado con lecciones estructuradas, ejemplos paso a paso y ejercicios prácticos alineados al currículo CBT.'),
            ('🤝', 'ACOMPAÑA', 'Realiza monitorización continua del progreso académico y envía alertas proactivas ante dificultades detectadas.'),
            ('🏆', 'MOTIVA', 'Implementa un sistema de gamificación con insignias, niveles de logro y reconocimientos por metas cumplidas.')
        ]
        
        for icon, title_text, description in features:
            feature_card = self.create_feature_card(icon, title_text, description)
            features_container.add_widget(feature_card)
        
        scroll.add_widget(features_container)
        
        # Botón para comenzar
        start_btn = Button(
            text='COMENZAR AHORA',
            size_hint_y=0.1,
            background_color=[0.2, 0.6, 0.9, 1],
            color=[1, 1, 1, 1],
            font_size=18,
            bold=True
        )
        start_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'student_registration'))
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        layout.add_widget(start_btn)
        self.add_widget(layout)
    
    def create_feature_card(self, icon, title_text, description):
        """Crea una tarjeta de característica"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            padding=20,
            spacing=15
        )
        
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        # Header de la tarjeta
        header = BoxLayout(size_hint_y=0.3)
        icon_label = Label(
            text=icon,
            font_size=32,
            size_hint_x=0.2
        )
        title_label = Label(
            text=title_text,
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            halign='left'
        )
        header.add_widget(icon_label)
        header.add_widget(title_label)
        
        # Descripción
        desc_label = Label(
            text=description,
            font_size=14,
            color=[0.4, 0.4, 0.4, 1],
            halign='left',
            valign='top'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        card.add_widget(header)
        card.add_widget(desc_label)
        return card

class DashboardScreen(Screen):
    """Dashboard principal del estudiante"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cbt_system = CBTLearningSystem()
        self.db = CBTMathDatabase()
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = self.create_header()
        
        # Contenido principal
        main_scroll = ScrollView()
        self.main_content = BoxLayout(
            orientation='vertical',
            spacing=25,
            size_hint_y=None,
            padding=25
        )
        self.main_content.bind(minimum_height=self.main_content.setter('height'))
        
        main_scroll.add_widget(self.main_content)
        
        # Barra de navegación inferior
        nav_bar = self.create_navigation_bar()
        
        layout.add_widget(self.header)
        layout.add_widget(main_scroll)
        layout.add_widget(nav_bar)
        self.add_widget(layout)
    
    def on_pre_enter(self):
        """Actualiza el dashboard cuando se entra"""
        self.update_dashboard()
    
    def create_header(self):
        """Crea el encabezado del dashboard"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            padding=[25, 10],
            spacing=20
        )
        
        # Información del estudiante
        student_box = BoxLayout(orientation='vertical')
        self.student_name_label = Label(
            text='Estudiante',
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            halign='left'
        )
        self.student_level_label = Label(
            text='Nivel: Básico',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            halign='left'
        )
        
        student_box.add_widget(self.student_name_label)
        student_box.add_widget(self.student_level_label)
        
        # Progreso
        progress_box = BoxLayout(orientation='vertical', size_hint_x=0.4)
        self.progress_label = Label(
            text='Progreso: 0%',
            font_size=16,
            color=[0.2, 0.6, 0.9, 1],
            halign='right'
        )
        progress_box.add_widget(self.progress_label)
        
        header.add_widget(student_box)
        header.add_widget(progress_box)
        return header
    
    def create_navigation_bar(self):
        """Crea la barra de navegación inferior"""
        nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.1,
            spacing=5,
            padding=10
        )
        
        nav_items = [
            ('🏠', 'Inicio', 'dashboard'),
            ('📚', 'Aprender', 'competences'),
            ('📊', 'Progreso', 'progress'),
            ('⚙️', 'Ajustes', 'settings')
        ]
        
        for icon, text, screen_name in nav_items:
            nav_btn = Button(
                text=f'{icon}\n{text}',
                font_size=11,
                background_color=[0.2, 0.6, 0.9, 0.1] if screen_name == 'dashboard' else [0.9, 0.9, 0.9, 1],
                color=[0.2, 0.2, 0.2, 1],
                border_radius=10
            )
            nav_btn.bind(on_press=lambda x, scr=screen_name: self.navigate_to(scr))
            nav.add_widget(nav_btn)
        
        return nav
    
    def navigate_to(self, screen_name):
        """Navega a una pantalla específica"""
        self.manager.current = screen_name
    
    def update_dashboard(self):
        """Actualiza el contenido del dashboard"""
        self.main_content.clear_widgets()
        
        app = App.get_running_app()
        student_data = getattr(app, 'student_data', {})
        
        # Actualizar header
        self.student_name_label.text = student_data.get('name', 'Estudiante')
        self.student_level_label.text = f'Nivel: {student_data.get("level", "Básico").capitalize()}'
        
        # Saludo personalizado
        welcome_card = self.create_welcome_card(student_data)
        self.main_content.add_widget(welcome_card)
        
        # Competencias activas
        competences_card = self.create_competences_card(student_data.get('level', 'basic'))
        self.main_content.add_widget(competences_card)
        
        # Próximas actividades
        activities_card = self.create_activities_card()
        self.main_content.add_widget(activities_card)
        
        # Estadísticas rápidas
        stats_card = self.create_stats_card()
        self.main_content.add_widget(stats_card)
    
    def create_welcome_card(self, student_data):
        """Crea tarjeta de bienvenida personalizada"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            padding=25,
            spacing=10
        )
        
        with card.canvas.before:
            Color(0.2, 0.6, 0.9, 0.1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        greeting = Label(
            text=f'¡Hola, {student_data.get("name", "Estudiante")}!',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        message = Label(
            text='Tu viaje de aprendizaje matemático comienza hoy.',
            font_size=16,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        card.add_widget(greeting)
        card.add_widget(message)
        return card
    
    def create_competences_card(self, level):
        """Crea tarjeta de competencias activas"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=250,
            padding=[25, 20],
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='COMPETENCIAS ACTIVAS',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            size_hint_y=0.2
        )
        
        # Lista de competencias
        competences_scroll = ScrollView(size_hint_y=0.8)
        competences_list = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        competences_list.bind(minimum_height=competences_list.setter('height'))
        
        level_data = self.cbt_system.levels.get(level, {})
        
        for competence_name, competence_data in level_data.items():
            competence_item = self.create_competence_item(competence_name, competence_data)
            competences_list.add_widget(competence_item)
        
        competences_scroll.add_widget(competences_list)
        
        card.add_widget(title)
        card.add_widget(competences_scroll)
        return card
    
    def create_competence_item(self, name, data):
        """Crea un ítem de competencia"""
        item = Button(
            size_hint_y=None,
            height=70,
            background_color=data.get('color', [0.9, 0.9, 0.9, 1]),
            color=[1, 1, 1, 1],
            border_radius=10,
            background_normal=''
        )
        
        content = BoxLayout(padding=15)
        
        # Información de la competencia
        info_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        name_label = Label(
            text=name,
            font_size=16,
            bold=True,
            color=[1, 1, 1, 1],
            halign='left'
        )
        
        code_label = Label(
            text=data.get('code', ''),
            font_size=12,
            color=[0.9, 0.9, 0.9, 1],
            halign='left'
        )
        
        info_box.add_widget(name_label)
        info_box.add_widget(code_label)
        
        # Botón de práctica
        practice_btn = Button(
            text='PRACTICAR',
            size_hint_x=0.3,
            background_color=[1, 1, 1, 0.3],
            color=[1, 1, 1, 1],
            font_size=12
        )
        practice_btn.bind(on_press=lambda x, n=name: self.start_practice(n))
        
        content.add_widget(info_box)
        content.add_widget(practice_btn)
        
        item.add_widget(content)
        return item
    
    def create_activities_card(self):
        """Crea tarjeta de próximas actividades"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            padding=[25, 20],
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='PRÓXIMAS ACTIVIDADES',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            size_hint_y=0.2
        )
        
        # Actividades
        activities = [
            ('📝', 'Evaluación diagnóstica', 'Hoy'),
            ('📚', 'Lección: Fracciones básicas', 'Mañana'),
            ('🎯', 'Práctica guiada', 'En 2 días'),
            ('🏆', 'Desafío especial', 'Esta semana')
        ]
        
        activities_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.8)
        
        for icon, activity, date in activities:
            activity_item = BoxLayout(size_hint_y=None, height=40)
            
            icon_label = Label(text=icon, font_size=20, size_hint_x=0.1)
            activity_label = Label(
                text=activity,
                font_size=14,
                color=[0.4, 0.4, 0.4, 1],
                halign='left',
                size_hint_x=0.7
            )
            date_label = Label(
                text=date,
                font_size=12,
                color=[0.6, 0.6, 0.6, 1],
                size_hint_x=0.2
            )
            
            activity_item.add_widget(icon_label)
            activity_item.add_widget(activity_label)
            activity_item.add_widget(date_label)
            activities_box.add_widget(activity_item)
        
        card.add_widget(title)
        card.add_widget(activities_box)
        return card
    
    def create_stats_card(self):
        """Crea tarjeta de estadísticas rápidas"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            padding=[25, 20],
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='TUS ESTADÍSTICAS',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            size_hint_y=0.2
        )
        
        # Grid de estadísticas
        stats_grid = GridLayout(cols=2, rows=2, spacing=20, size_hint_y=0.8)
        
        stats = [
            ('🎯', 'Precisión', '85%'),
            ('⏱️', 'Tiempo promedio', '45s'),
            ('📈', 'Progreso semanal', '+12%'),
            ('🏆', 'Logros', '3/10')
        ]
        
        for icon, label, value in stats:
            stat_box = BoxLayout(orientation='vertical')
            
            stat_icon = Label(text=icon, font_size=24)
            stat_label = Label(text=label, font_size=12, color=[0.5, 0.5, 0.5, 1])
            stat_value = Label(text=value, font_size=18, bold=True, color=[0.2, 0.6, 0.9, 1])
            
            stat_box.add_widget(stat_icon)
            stat_box.add_widget(stat_label)
            stat_box.add_widget(stat_value)
            
            stats_grid.add_widget(stat_box)
        
        card.add_widget(title)
        card.add_widget(stats_grid)
        return card
    
    def start_practice(self, competence_name):
        """Inicia práctica de una competencia"""
        app = App.get_running_app()
        app.current_competence = competence_name
        self.manager.current = 'practice'

class CompetencesScreen(Screen):
    """Pantalla de selección de competencias"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cbt_system = CBTLearningSystem()
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            font_size=24,
            background_color=[0.8, 0.8, 0.8, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        )
        
        self.title_label = Label(
            text='COMPETENCIAS CBT',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        
        # Selector de nivel
        level_selector = BoxLayout(size_hint_y=0.1, spacing=10, padding=[20, 5])
        
        levels = ['Básico', 'Medio', 'Medio Superior', 'Avanzado']
        self.level_buttons = {}
        
        for level in levels:
            btn = Button(
                text=level,
                background_color=[0.2, 0.6, 0.9, 0.3] if level == 'Básico' else [0.9, 0.9, 0.9, 1],
                color=[0.2, 0.2, 0.2, 1],
                font_size=12
            )
            btn.bind(on_press=lambda x, l=level.lower(): self.select_level(l))
            self.level_buttons[level] = btn
            level_selector.add_widget(btn)
        
        # Contenido de competencias
        scroll = ScrollView()
        self.competences_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None,
            padding=25
        )
        self.competences_container.bind(minimum_height=self.competences_container.setter('height'))
        
        scroll.add_widget(self.competences_container)
        
        layout.add_widget(header)
        layout.add_widget(level_selector)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_pre_enter(self):
        """Carga las competencias al entrar"""
        app = App.get_running_app()
        level = app.student_data.get('level', 'basic') if hasattr(app, 'student_data') else 'basic'
        self.load_competences(level)
    
    def select_level(self, level):
        """Selecciona un nivel de competencias"""
        level_map = {
            'básico': 'basic',
            'medio': 'medium',
            'medio superior': 'high',
            'avanzado': 'advanced'
        }
        
        level_key = level_map.get(level, 'basic')
        self.load_competences(level_key)
        
        # Actualizar botones
        for name, btn in self.level_buttons.items():
            btn.background_color = [0.2, 0.6, 0.9, 0.3] if name.lower() == level else [0.9, 0.9, 0.9, 1]
    
    def load_competences(self, level):
        """Carga las competencias del nivel seleccionado"""
        self.competences_container.clear_widgets()
        
        competences = self.cbt_system.levels.get(level, {})
        
        for name, data in competences.items():
            competence_card = self.create_competence_card(name, data)
            self.competences_container.add_widget(competence_card)
    
    def create_competence_card(self, name, data):
        """Crea una tarjeta de competencia detallada"""
        card = Button(
            size_hint_y=None,
            height=200,
            background_color=data.get('color', [0.2, 0.6, 0.9, 1]),
            color=[1, 1, 1, 1],
            border_radius=20,
            background_normal=''
        )
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Encabezado
        header = BoxLayout(size_hint_y=0.3)
        code_label = Label(
            text=data.get('code', ''),
            font_size=14,
            color=[0.9, 0.9, 0.9, 1],
            size_hint_x=0.4
        )
        name_label = Label(
            text=name,
            font_size=20,
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_x=0.6,
            halign='left'
        )
        header.add_widget(code_label)
        header.add_widget(name_label)
        
        # Descripción
        desc_label = Label(
            text=data.get('description', ''),
            font_size=14,
            color=[0.95, 0.95, 0.95, 1],
            halign='left',
            valign='top',
            size_hint_y=0.4
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        # Subtemas
        subtopics_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=0.3)
        
        for subtopic in data.get('subtopics', [])[:2]:  # Mostrar primeros 2
            subtopic_label = Label(
                text=f"• {subtopic}",
                font_size=12,
                color=[0.9, 0.9, 0.9, 0.9],
                halign='left',
                size_hint_y=None,
                height=20
            )
            subtopics_box.add_widget(subtopic_label)
        
        if len(data.get('subtopics', [])) > 2:
            more_label = Label(
                text=f"+ {len(data.get('subtopics', [])) - 2} más...",
                font_size=11,
                color=[0.9, 0.9, 0.9, 0.7],
                italic=True
            )
            subtopics_box.add_widget(more_label)
        
        content.add_widget(header)
        content.add_widget(desc_label)
        content.add_widget(subtopics_box)
        card.add_widget(content)
        
        card.bind(on_press=lambda x, n=name: self.select_competence(n))
        return card
    
    def select_competence(self, competence_name):
        """Selecciona una competencia para practicar"""
        app = App.get_running_app()
        app.current_competence = competence_name
        self.manager.current = 'practice'

class PracticeScreen(Screen):
    """Pantalla de práctica de competencias CBT"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = CBTMathDatabase()
        self.current_exercise = None
        self.start_time = None
        self.correct_count = 0
        self.total_count = 0
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            font_size=24,
            background_color=[0.8, 0.8, 0.8, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'competences')
        )
        
        self.competence_label = Label(
            text='PRÁCTICA',
            font_size=22,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        header.add_widget(back_btn)
        header.add_widget(self.competence_label)
        
        # Información del ejercicio
        self.exercise_info = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.08,
            spacing=10
        )
        
        self.exercise_counter = Label(
            text='Ejercicio: 1/10',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        self.timer_label = Label(
            text='Tiempo: 00:00',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        self.exercise_info.add_widget(self.exercise_counter)
        self.exercise_info.add_widget(self.timer_label)
        
        # Área de la pregunta
        self.question_area = BoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            padding=[20, 10]
        )
        
        with self.question_area.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=self.question_area.pos, size=self.question_area.size, radius=[15])
        
        self.question_label = Label(
            text='',
            font_size=22,
            bold=True,
            color=[0.2, 0.2, 0.2, 1],
            halign='center',
            valign='middle'
        )
        self.question_label.bind(size=self.question_label.setter('text_size'))
        
        self.question_area.add_widget(self.question_label)
        
        # Opciones de respuesta
        self.options_container = GridLayout(cols=2, rows=2, spacing=15, size_hint_y=0.4)
        
        # Input para respuesta numérica
        self.numeric_input = TextInput(
            hint_text='Escribe tu respuesta aquí...',
            multiline=False,
            font_size=20,
            size_hint_y=0.15,
            background_color=[1, 1, 1, 1],
            foreground_color=[0.2, 0.2, 0.2, 1],
            padding=[20, 15],
            opacity=0
        )
        
        # Botones de acción
        action_buttons = BoxLayout(size_hint_y=0.12, spacing=15)
        
        check_btn = Button(
            text='VERIFICAR',
            background_color=[0.2, 0.8, 0.4, 1],
            color=[1, 1, 1, 1],
            font_size=16
        )
        check_btn.bind(on_press=self.check_answer)
        
        hint_btn = Button(
            text='PISTA',
            background_color=[0.96, 0.77, 0.23, 1],
            color=[1, 1, 1, 1],
            font_size=16
        )
        hint_btn.bind(on_press=self.show_hint)
        
        skip_btn = Button(
            text='SALTAR',
            background_color=[0.8, 0.8, 0.8, 1],
            color=[0.2, 0.2, 0.2, 1],
            font_size=16
        )
        skip_btn.bind(on_press=self.next_exercise)
        
        action_buttons.add_widget(check_btn)
        action_buttons.add_widget(hint_btn)
        action_buttons.add_widget(skip_btn)
        
        # Resultado
        self.result_label = Label(
            text='',
            font_size=16,
            color=[0.5, 0.5, 0.5, 1],
            halign='center',
            size_hint_y=0.1
        )
        
        layout.add_widget(header)
        layout.add_widget(self.exercise_info)
        layout.add_widget(self.question_area)
        layout.add_widget(self.options_container)
        layout.add_widget(self.numeric_input)
        layout.add_widget(action_buttons)
        layout.add_widget(self.result_label)
        
        self.add_widget(layout)
    
    def on_pre_enter(self):
        """Prepara la práctica al entrar"""
        app = App.get_running_app()
        self.current_competence = getattr(app, 'current_competence', 'Aritmética Fundamental')
        self.competence_label.text = self.current_competence
        self.correct_count = 0
        self.total_count = 0
        self.start_time = datetime.now()
        self.generate_exercise()
        Clock.schedule_interval(self.update_timer, 1)
    
    def update_timer(self, dt):
        """Actualiza el temporizador"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            minutes = elapsed.seconds // 60
            seconds = elapsed.seconds % 60
            self.timer_label.text = f'Tiempo: {minutes:02d}:{seconds:02d}'
    
    def generate_exercise(self):
        """Genera un ejercicio basado en la competencia"""
        self.total_count += 1
        self.exercise_counter.text = f'Ejercicio: {self.total_count}/10'
        
        # Determinar tipo de ejercicio basado en la competencia
        if 'Aritmética' in self.current_competence:
            self.generate_arithmetic_exercise()
        elif 'Geometría' in self.current_competence:
            self.generate_geometry_exercise()
        elif 'Álgebra' in self.current_competence:
            self.generate_algebra_exercise()
        else:
            self.generate_general_exercise()
        
        self.start_time = datetime.now()
        self.result_label.text = ''
    
    def generate_arithmetic_exercise(self):
        """Genera ejercicio de aritmética"""
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        operation = random.choice(['+', '-', '×', '÷'])
        
        if operation == '+':
            question = f'{a} + {b} = ?'
            answer = a + b
        elif operation == '-':
            question = f'{a} - {b} = ?'
            answer = a - b
        elif operation == '×':
            question = f'{a} × {b} = ?'
            answer = a * b
        else:  # ÷
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)
            question = f'{a} ÷ {b} = ?'
            answer = a // b
        
        self.current_exercise = {
            'question': question,
            'answer': answer,
            'type': 'numeric'
        }
        
        self.question_label.text = question
        self.numeric_input.opacity = 1
        self.options_container.opacity = 0
        self.numeric_input.text = ''
    
    def generate_geometry_exercise(self):
        """Genera ejercicio de geometría"""
        exercises = [
            ('Calcula el perímetro de un cuadrado de lado {} cm', 
             lambda x: 4 * x, random.randint(5, 20)),
            ('Calcula el área de un triángulo con base {} cm y altura {} cm',
             lambda b, h: b * h / 2, random.randint(5, 15), random.randint(5, 15)),
            ('Calcula el área de un rectángulo de base {} cm y altura {} cm',
             lambda b, h: b * h, random.randint(5, 20), random.randint(5, 15))
        ]
        
        exercise = random.choice(exercises)
        if len(exercise) == 3:
            question = exercise[0].format(exercise[2])
            answer = exercise[1](exercise[2])
        else:
            question = exercise[0].format(exercise[2], exercise[3])
            answer = exercise[1](exercise[2], exercise[3])
        
        self.current_exercise = {
            'question': question,
            'answer': answer,
            'type': 'numeric'
        }
        
        self.question_label.text = question
        self.numeric_input.opacity = 1
        self.options_container.opacity = 0
        self.numeric_input.text = ''
    
    def generate_algebra_exercise(self):
        """Genera ejercicio de álgebra"""
        a = random.randint(1, 10)
        b = random.randint(1, 20)
        c = random.randint(10, 50)
        
        question = f'Resuelve para x: {a}x + {b} = {c}'
        answer = (c - b) / a
        
        # Crear opciones múltiples
        options = [round(answer, 2)]
        while len(options) < 4:
            option = round(answer + random.uniform(-3, 3), 2)
            if option not in options:
                options.append(option)
        
        random.shuffle(options)
        correct_index = options.index(round(answer, 2))
        
        self.current_exercise = {
            'question': question,
            'answer': round(answer, 2),
            'type': 'multiple_choice',
            'options': options,
            'correct_index': correct_index
        }
        
        self.question_label.text = question
        self.numeric_input.opacity = 0
        self.options_container.opacity = 1
        
        # Limpiar y llenar opciones
        self.options_container.clear_widgets()
        self.selected_option = None
        
        for i, option in enumerate(options):
            btn = Button(
                text=str(option),
                font_size=18,
                background_color=[0.9, 0.9, 0.9, 1],
                color=[0.2, 0.2, 0.2, 1]
            )
            btn.bind(on_press=lambda x, idx=i: self.select_option(idx))
            self.options_container.add_widget(btn)
    
    def generate_general_exercise(self):
        """Genera ejercicio general"""
        self.generate_arithmetic_exercise()
    
    def select_option(self, index):
        """Selecciona una opción en preguntas de opción múltiple"""
        self.selected_option = index
        
        # Resaltar opción seleccionada
        for i, child in enumerate(self.options_container.children):
            if i == index:
                child.background_color = [0.2, 0.6, 0.9, 1]
                child.color = [1, 1, 1, 1]
            else:
                child.background_color = [0.9, 0.9, 0.9, 1]
                child.color = [0.2, 0.2, 0.2, 1]
    
    def check_answer(self, instance):
        """Verifica la respuesta del usuario"""
        if not self.current_exercise:
            return
        
        correct = False
        user_answer = ''
        
        if self.current_exercise['type'] == 'numeric':
            try:
                user_answer = float(self.numeric_input.text)
                correct = abs(user_answer - self.current_exercise['answer']) < 0.01
            except:
                self.result_label.text = 'Por favor ingresa un número válido'
                self.result_label.color = [0.96, 0.77, 0.23, 1]
                return
        
        elif self.current_exercise['type'] == 'multiple_choice':
            if self.selected_option is None:
                self.result_label.text = 'Por favor selecciona una opción'
                self.result_label.color = [0.96, 0.77, 0.23, 1]
                return
            
            user_answer = self.current_exercise['options'][self.selected_option]
            correct = (self.selected_option == self.current_exercise['correct_index'])
        
        if correct:
            self.correct_count += 1
            self.result_label.text = f'✅ ¡Correcto! Respuesta: {self.current_exercise["answer"]}'
            self.result_label.color = [0.2, 0.8, 0.4, 1]
            self.celebrate_success()
        else:
            self.result_label.text = f'❌ Incorrecto. La respuesta correcta es: {self.current_exercise["answer"]}'
            self.result_label.color = [0.9, 0.3, 0.3, 1]
        
        # Siguiente ejercicio después de 2 segundos
        Clock.schedule_once(lambda dt: self.next_exercise(None), 2)
    
    def show_hint(self, instance):
        """Muestra una pista"""
        hints = {
            'Aritmética': 'Recuerda el orden de las operaciones y verifica tus cálculos.',
            'Geometría': 'Dibuja la figura en tu mente y aplica las fórmulas correctas.',
            'Álgebra': 'Aísla la variable realizando operaciones inversas en ambos lados.',
            'General': 'Lee cuidadosamente el problema y divide en pasos pequeños.'
        }
        
        hint_key = next((key for key in hints.keys() if key in self.current_competence), 'General')
        
        popup = ModalView(size_hint=(0.8, 0.3))
        content = BoxLayout(orientation='vertical', padding=20)
        
        content.add_widget(Label(
            text='💡 PISTA',
            font_size=20,
            bold=True,
            color=[0.96, 0.77, 0.23, 1]
        ))
        
        content.add_widget(Label(
            text=hints[hint_key],
            font_size=16,
            halign='center'
        ))
        
        ok_btn = Button(
            text='ENTENDIDO',
            size_hint_y=0.3,
            background_color=[0.96, 0.77, 0.23, 1],
            color=[1, 1, 1, 1]
        )
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(ok_btn)
        popup.add_widget(content)
        popup.open()
    
    def next_exercise(self, instance):
        """Genera el siguiente ejercicio"""
        if self.total_count >= 10:
            self.show_results()
        else:
            self.generate_exercise()
    
    def celebrate_success(self):
        """Animación de celebración"""
        anim = Animation(
            background_color=[0.2, 0.8, 0.4, 0.3],
            duration=0.3
        ) + Animation(
            background_color=[1, 1, 1, 1],
            duration=0.3
        )
        anim.start(self.question_area)
    
    def show_results(self):
        """Muestra los resultados finales"""
        accuracy = (self.correct_count / 10) * 100
        elapsed = datetime.now() - self.start_time
        minutes = elapsed.seconds // 60
        seconds = elapsed.seconds % 60
        
        popup = ModalView(size_hint=(0.9, 0.7))
        content = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Título
        title = Label(
            text='🏆 RESULTADOS DE LA PRÁCTICA',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Competencia
        competence_label = Label(
            text=f'Competencia: {self.current_competence}',
            font_size=18,
            color=[0.4, 0.4, 0.4, 1]
        )
        
        # Estadísticas
        stats_box = BoxLayout(orientation='vertical', spacing=15)
        
        stats = [
            ('✅', 'Respuestas correctas', f'{self.correct_count}/10'),
            ('📊', 'Precisión', f'{accuracy:.1f}%'),
            ('⏱️', 'Tiempo total', f'{minutes:02d}:{seconds:02d}'),
            ('🎯', 'Puntuación', f'{self.correct_count * 10} puntos')
        ]
        
        for icon, label, value in stats:
            stat_row = BoxLayout(size_hint_y=None, height=50)
            
            icon_label = Label(text=icon, font_size=24, size_hint_x=0.2)
            label_label = Label(text=label, font_size=16, color=[0.5, 0.5, 0.5, 1], size_hint_x=0.5, halign='left')
            value_label = Label(text=value, font_size=18, bold=True, color=[0.2, 0.6, 0.9, 1], size_hint_x=0.3)
            
            stat_row.add_widget(icon_label)
            stat_row.add_widget(label_label)
            stat_row.add_widget(value_label)
            stats_box.add_widget(stat_row)
        
        # Mensaje motivacional
        if accuracy >= 80:
            message = '¡Excelente trabajo! Dominas esta competencia.'
            color = [0.2, 0.8, 0.4, 1]
        elif accuracy >= 60:
            message = 'Buen trabajo. Sigue practicando para mejorar.'
            color = [0.96, 0.77, 0.23, 1]
        else:
            message = 'Necesitas más práctica. Revisa los conceptos básicos.'
            color = [0.9, 0.3, 0.3, 1]
        
        message_label = Label(
            text=message,
            font_size=16,
            color=color,
            bold=True
        )
        
        # Botones
        buttons_box = BoxLayout(size_hint_y=0.2, spacing=15)
        
        retry_btn = Button(
            text='REPETIR PRÁCTICA',
            background_color=[0.2, 0.6, 0.9, 1],
            color=[1, 1, 1, 1]
        )
        retry_btn.bind(on_press=lambda x: (popup.dismiss(), self.reset_practice()))
        
        dashboard_btn = Button(
            text='VOLVER AL INICIO',
            background_color=[0.8, 0.8, 0.8, 1],
            color=[0.2, 0.2, 0.2, 1]
        )
        dashboard_btn.bind(on_press=lambda x: (popup.dismiss(), setattr(self.manager, 'current', 'dashboard')))
        
        buttons_box.add_widget(retry_btn)
        buttons_box.add_widget(dashboard_btn)
        
        content.add_widget(title)
        content.add_widget(competence_label)
        content.add_widget(stats_box)
        content.add_widget(message_label)
        content.add_widget(buttons_box)
        
        popup.add_widget(content)
        popup.open()
    
    def reset_practice(self):
        """Reinicia la práctica"""
        self.correct_count = 0
        self.total_count = 0
        self.start_time = datetime.now()
        self.generate_exercise()

class ProgressScreen(Screen):
    """Pantalla de progreso y estadísticas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            font_size=24,
            background_color=[0.8, 0.8, 0.8, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        )
        
        title = Label(
            text='MI PROGRESO',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # Contenido
        scroll = ScrollView()
        self.progress_container = BoxLayout(
            orientation='vertical',
            spacing=25,
            size_hint_y=None,
            padding=25
        )
        self.progress_container.bind(minimum_height=self.progress_container.setter('height'))
        
        scroll.add_widget(self.progress_container)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_pre_enter(self):
        self.load_progress_data()
    
    def load_progress_data(self):
        """Carga los datos de progreso"""
        self.progress_container.clear_widgets()
        
        # Tarjeta de progreso general
        general_card = self.create_general_progress_card()
        self.progress_container.add_widget(general_card)
        
        # Estadísticas detalladas
        stats_card = self.create_detailed_stats_card()
        self.progress_container.add_widget(stats_card)
        
        # Historial de práctica
        history_card = self.create_practice_history_card()
        self.progress_container.add_widget(history_card)
        
        # Logros
        achievements_card = self.create_achievements_card()
        self.progress_container.add_widget(achievements_card)
    
    def create_general_progress_card(self):
        """Crea tarjeta de progreso general"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            padding=25,
            spacing=15
        )
        
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        title = Label(
            text='📊 PROGRESO GENERAL',
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Barra de progreso
        progress_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.6)
        
        progress_label = Label(
            text='45% completado',
            font_size=16,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        # Barra visual
        bar_container = BoxLayout(size_hint_y=0.3)
        with bar_container.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            RoundedRectangle(pos=bar_container.pos, size=bar_container.size, radius=[10])
            Color(0.2, 0.6, 0.9, 1)
            RoundedRectangle(
                pos=bar_container.pos, 
                size=[bar_container.size[0] * 0.45, bar_container.size[1]], 
                radius=[10]
            )
        
        progress_box.add_widget(progress_label)
        progress_box.add_widget(bar_container)
        
        # Meta próxima
        next_goal = Label(
            text='Próxima meta: Completar 60% de las competencias básicas',
            font_size=14,
            color=[0.6, 0.6, 0.6, 1]
        )
        
        card.add_widget(title)
        card.add_widget(progress_box)
        card.add_widget(next_goal)
        return card
    
    def create_detailed_stats_card(self):
        """Crea tarjeta de estadísticas detalladas"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=300,
            padding=25,
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='📈 ESTADÍSTICAS DETALLADAS',
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Grid de estadísticas
        stats_grid = GridLayout(cols=2, rows=3, spacing=20, size_hint_y=0.8)
        
        stats = [
            ('🎯', 'Precisión promedio', '78%'),
            ('⏱️', 'Tiempo promedio por ejercicio', '45s'),
            ('📚', 'Ejercicios completados', '124'),
            ('🏆', 'Competencias dominadas', '3/15'),
            ('📅', 'Días activos consecutivos', '7'),
            ('⭐', 'Puntuación total', '1,240')
        ]
        
        for icon, label, value in stats:
            stat_box = BoxLayout(orientation='vertical', spacing=5)
            
            stat_header = BoxLayout(size_hint_y=0.4)
            stat_icon = Label(text=icon, font_size=20)
            stat_label = Label(text=label, font_size=12, color=[0.5, 0.5, 0.5, 1], halign='left')
            
            stat_header.add_widget(stat_icon)
            stat_header.add_widget(stat_label)
            
            stat_value = Label(text=value, font_size=18, bold=True, color=[0.2, 0.6, 0.9, 1])
            
            stat_box.add_widget(stat_header)
            stat_box.add_widget(stat_value)
            stats_grid.add_widget(stat_box)
        
        card.add_widget(title)
        card.add_widget(stats_grid)
        return card
    
    def create_practice_history_card(self):
        """Crea tarjeta de historial de práctica"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=250,
            padding=[25, 20],
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='📅 HISTORIAL DE PRÁCTICA',
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Lista de sesiones recientes
        sessions_scroll = ScrollView(size_hint_y=0.8)
        sessions_list = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        sessions_list.bind(minimum_height=sessions_list.setter('height'))
        
        sessions = [
            ('Hoy', 'Aritmética Fundamental', '15 ejercicios', '85%'),
            ('Ayer', 'Geometría Elemental', '12 ejercicios', '75%'),
            ('2 días', 'Álgebra Básica', '10 ejercicios', '90%'),
            ('3 días', 'Repaso General', '20 ejercicios', '80%')
        ]
        
        for date, topic, exercises, accuracy in sessions:
            session_item = self.create_session_item(date, topic, exercises, accuracy)
            sessions_list.add_widget(session_item)
        
        sessions_scroll.add_widget(sessions_list)
        
        card.add_widget(title)
        card.add_widget(sessions_scroll)
        return card
    
    def create_session_item(self, date, topic, exercises, accuracy):
        """Crea un ítem de sesión de práctica"""
        item = BoxLayout(
            size_hint_y=None,
            height=60,
            spacing=15,
            padding=[0, 10]
        )
        
        date_label = Label(
            text=date,
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.2
        )
        
        topic_label = Label(
            text=topic,
            font_size=16,
            color=[0.3, 0.3, 0.3, 1],
            halign='left',
            size_hint_x=0.4
        )
        
        exercises_label = Label(
            text=exercises,
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.25
        )
        
        accuracy_label = Label(
            text=accuracy,
            font_size=16,
            bold=True,
            color=[0.2, 0.8, 0.4, 1] if float(accuracy[:-1]) >= 80 else [0.96, 0.77, 0.23, 1],
            size_hint_x=0.15
        )
        
        item.add_widget(date_label)
        item.add_widget(topic_label)
        item.add_widget(exercises_label)
        item.add_widget(accuracy_label)
        return item
    
    def create_achievements_card(self):
        """Crea tarjeta de logros"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=250,
            padding=[25, 20],
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='🏆 LOGROS OBTENIDOS',
            font_size=20,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Grid de logros
        achievements_grid = GridLayout(cols=3, rows=2, spacing=15, size_hint_y=0.8)
        
        achievements = [
            ('🥇', 'Primer ejercicio', 'Completado'),
            ('📚', '10 ejercicios', 'Completado'),
            ('🎯', 'Precisión 80%', 'Completado'),
            ('⏱️', 'Rápido y preciso', 'En progreso'),
            ('🏅', 'Competencia maestra', 'Por alcanzar'),
            ('⭐', 'Estrella matemática', 'Por alcanzar')
        ]
        
        for icon, name, status in achievements:
            achievement_box = BoxLayout(orientation='vertical', spacing=5)
            
            achievement_icon = Label(text=icon, font_size=24)
            achievement_name = Label(text=name, font_size=12, color=[0.5, 0.5, 0.5, 1])
            
            status_color = [0.2, 0.8, 0.4, 1] if status == 'Completado' else [0.96, 0.77, 0.23, 1]
            achievement_status = Label(text=status, font_size=11, color=status_color)
            
            achievement_box.add_widget(achievement_icon)
            achievement_box.add_widget(achievement_name)
            achievement_box.add_widget(achievement_status)
            achievements_grid.add_widget(achievement_box)
        
        card.add_widget(title)
        card.add_widget(achievements_grid)
        return card

class SettingsScreen(Screen):
    """Pantalla de ajustes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            font_size=24,
            background_color=[0.8, 0.8, 0.8, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        )
        
        title = Label(
            text='AJUSTES',
            font_size=24,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # Contenido
        scroll = ScrollView()
        settings_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None,
            padding=25
        )
        settings_container.bind(minimum_height=settings_container.setter('height'))
        
        # Sección de perfil
        profile_card = self.create_profile_card()
        settings_container.add_widget(profile_card)
        
        # Sección de preferencias
        preferences_card = self.create_preferences_card()
        settings_container.add_widget(preferences_card)
        
        # Sección de ayuda
        help_card = self.create_help_card()
        settings_container.add_widget(help_card)
        
        # Sección de información
        info_card = self.create_info_card()
        settings_container.add_widget(info_card)
        
        scroll.add_widget(settings_container)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_profile_card(self):
        """Crea tarjeta de perfil"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            padding=25,
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        title = Label(
            text='👤 PERFIL DEL ESTUDIANTE',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        app = App.get_running_app()
        student_data = getattr(app, 'student_data', {})
        
        # Información del estudiante
        info_box = BoxLayout(orientation='vertical', spacing=8)
        
        info_items = [
            ('Nombre', student_data.get('name', 'No registrado')),
            ('Edad', student_data.get('age', 'No especificada')),
            ('Grado', student_data.get('grade', 'No especificado')),
            ('Nivel', student_data.get('level', 'Básico').capitalize())
        ]
        
        for label, value in info_items:
            info_row = BoxLayout(size_hint_y=None, height=30)
            
            label_label = Label(
                text=f'{label}:',
                font_size=14,
                color=[0.5, 0.5, 0.5, 1],
                size_hint_x=0.4,
                halign='left'
            )
            
            value_label = Label(
                text=value,
                font_size=14,
                color=[0.3, 0.3, 0.3, 1],
                size_hint_x=0.6,
                halign='left'
            )
            
            info_row.add_widget(label_label)
            info_row.add_widget(value_label)
            info_box.add_widget(info_row)
        
        # Botón de editar
        edit_btn = Button(
            text='EDITAR PERFIL',
            size_hint_y=None,
            height=40,
            background_color=[0.2, 0.6, 0.9, 0.3],
            color=[0.2, 0.6, 0.9, 1],
            font_size=14
        )
        edit_btn.bind(on_press=self.edit_profile)
        
        card.add_widget(title)
        card.add_widget(info_box)
        card.add_widget(edit_btn)
        return card
    
    def create_preferences_card(self):
        """Crea tarjeta de preferencias"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=250,
            padding=25,
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='⚙️ PREFERENCIAS DE APRENDIZAJE',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Opciones de preferencias
        preferences_box = BoxLayout(orientation='vertical', spacing=15)
        
        # Nivel de dificultad
        difficulty_row = BoxLayout(size_hint_y=None, height=50)
        difficulty_label = Label(
            text='Dificultad predeterminada:',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.6,
            halign='left'
        )
        
        difficulty_selector = BoxLayout(size_hint_x=0.4, spacing=5)
        for diff in ['Fácil', 'Media', 'Difícil']:
            btn = Button(
                text=diff,
                font_size=12,
                background_color=[0.2, 0.6, 0.9, 0.3] if diff == 'Media' else [0.9, 0.9, 0.9, 1],
                color=[0.2, 0.2, 0.2, 1]
            )
            difficulty_selector.add_widget(btn)
        
        difficulty_row.add_widget(difficulty_label)
        difficulty_row.add_widget(difficulty_selector)
        
        # Cantidad de ejercicios
        exercises_row = BoxLayout(size_hint_y=None, height=50)
        exercises_label = Label(
            text='Ejercicios por sesión:',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.6,
            halign='left'
        )
        
        exercises_slider = Slider(min=5, max=20, value=10, size_hint_x=0.4)
        exercises_value = Label(text='10', font_size=14, size_hint_x=0.1)
        
        exercises_slider.bind(value=lambda slider, value: setattr(exercises_value, 'text', str(int(value))))
        
        exercises_row.add_widget(exercises_label)
        exercises_row.add_widget(exercises_slider)
        exercises_row.add_widget(exercises_value)
        
        # Sonidos
        sounds_row = BoxLayout(size_hint_y=None, height=40)
        sounds_label = Label(
            text='Efectos de sonido:',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.6,
            halign='left'
        )
        
        sounds_switch = Button(
            text='ON',
            size_hint_x=0.4,
            background_color=[0.2, 0.8, 0.4, 0.3],
            color=[0.2, 0.8, 0.4, 1]
        )
        sounds_switch.bind(on_press=lambda x: self.toggle_sound(sounds_switch))
        
        sounds_row.add_widget(sounds_label)
        sounds_row.add_widget(sounds_switch)
        
        preferences_box.add_widget(difficulty_row)
        preferences_box.add_widget(exercises_row)
        preferences_box.add_widget(sounds_row)
        
        card.add_widget(title)
        card.add_widget(preferences_box)
        return card
    
    def create_help_card(self):
        """Crea tarjeta de ayuda"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            padding=25,
            spacing=15
        )
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=[card.pos[0], card.pos[1]], size=[card.size[0], 2])
        
        title = Label(
            text='❓ AYUDA Y SOPORTE',
            font_size=18,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Opciones de ayuda
        help_options = BoxLayout(orientation='vertical', spacing=10)
        
        help_items = [
            ('📖', 'Manual de usuario', self.show_user_manual),
            ('📧', 'Contactar soporte', self.contact_support),
            ('🔄', 'Reiniciar progreso', self.reset_progress),
            ('ℹ️', 'Acerca de la app', self.show_about)
        ]
        
        for icon, text, action in help_items:
            help_btn = Button(
                text=f'{icon} {text}',
                size_hint_y=None,
                height=40,
                background_color=[0.95, 0.95, 0.95, 1],
                color=[0.3, 0.3, 0.3, 1],
                font_size=14,
                halign='left'
            )
            help_btn.bind(on_press=lambda x, act=action: act())
            help_options.add_widget(help_btn)
        
        card.add_widget(title)
        card.add_widget(help_options)
        return card
    
    def create_info_card(self):
        """Crea tarjeta de información"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            padding=25,
            spacing=10
        )
        
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        title = Label(
            text='ℹ️ INFORMACIÓN DE LA APLICACIÓN',
            font_size=16,
            bold=True,
            color=[0.2, 0.2, 0.2, 1]
        )
        
        version = Label(
            text='Versión: 5.0.0',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        copyright_text = Label(
            text='© 2024 ASMET CBT ACADEMYC',
            font_size=12,
            color=[0.6, 0.6, 0.6, 1]
        )
        
        card.add_widget(title)
        card.add_widget(version)
        card.add_widget(copyright_text)
        return card
    
    def edit_profile(self, instance):
        """Edita el perfil del estudiante"""
        self.manager.current = 'student_registration'
    
    def toggle_sound(self, button):
        """Alterna los efectos de sonido"""
        if button.text == 'ON':
            button.text = 'OFF'
            button.background_color = [0.9, 0.3, 0.3, 0.3]
            button.color = [0.9, 0.3, 0.3, 1]
        else:
            button.text = 'ON'
            button.background_color = [0.2, 0.8, 0.4, 0.3]
            button.color = [0.2, 0.8, 0.4, 1]
    
    def show_user_manual(self):
        """Muestra el manual de usuario"""
        self.show_message('Manual de usuario', 'Accede al manual completo desde nuestro sitio web.')
    
    def contact_support(self):
        """Contacta con soporte"""
        self.show_message('Soporte', 'Envía un correo a: soporte@asmet-cbt.academyc')
    
    def reset_progress(self):
        """Reinicia el progreso"""
        popup = ModalView(size_hint=(0.8, 0.3))
        content = BoxLayout(orientation='vertical', padding=20)
        
        content.add_widget(Label(
            text='⚠️ ¿Reiniciar progreso?',
            font_size=18,
            bold=True,
            color=[0.96, 0.77, 0.23, 1]
        ))
        
        content.add_widget(Label(
            text='Esta acción eliminará todo tu progreso.',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1]
        ))
        
        buttons = BoxLayout(size_hint_y=0.4, spacing=10)
        
        cancel_btn = Button(
            text='CANCELAR',
            background_color=[0.8, 0.8, 0.8, 1],
            color=[0.2, 0.2, 0.2, 1]
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        confirm_btn = Button(
            text='CONFIRMAR',
            background_color=[0.9, 0.3, 0.3, 1],
            color=[1, 1, 1, 1]
        )
        confirm_btn.bind(on_press=lambda x: (popup.dismiss(), self.confirm_reset()))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        
        content.add_widget(buttons)
        popup.add_widget(content)
        popup.open()
    
    def confirm_reset(self):
        """Confirma el reinicio del progreso"""
        self.show_message('Progreso reiniciado', 'Tu progreso ha sido reiniciado exitosamente.')
    
    def show_about(self):
        """Muestra información acerca de la app"""
        about_text = '''ASMET CBT ACADEMYC v5.0

Una plataforma de aprendizaje matemático basada en Competencias Basadas en Tareas (CBT).

Características:
• Sistema adaptativo de aprendizaje
• Seguimiento personalizado del progreso
• Más de 100 competencias matemáticas
• Interfaz intuitiva y amigable

Desarrollado con pasión por la educación matemática.'''
        
        self.show_message('Acerca de', about_text)
    
    def show_message(self, title, message):
        """Muestra un mensaje emergente"""
        popup = ModalView(size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=20)
        
        content.add_widget(Label(
            text=title,
            font_size=20,
            bold=True,
            color=[0.2, 0.6, 0.9, 1]
        ))
        
        content.add_widget(Label(
            text=message,
            font_size=14,
            color=[0.5, 0.5, 0.5, 1],
            halign='center'
        ))
        
        ok_btn = Button(
            text='OK',
            size_hint_y=0.3,
            background_color=[0.2, 0.6, 0.9, 1],
            color=[1, 1, 1, 1]
        )
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(ok_btn)
        popup.add_widget(content)
        popup.open()

class ASMETCBTApp(App):
    """Aplicación principal ASMET CBT ACADEMYC"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ASMET CBT ACADEMYC"
        self.student_data = {}
        self.current_competence = ""
    
    def build(self):
        """Construye la aplicación"""
        sm = ScreenManager(transition=FadeTransition())
        
        # Registrar todas las pantallas
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(StudentRegistrationScreen(name='student_registration'))
        sm.add_widget(FeaturesScreen(name='features'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(CompetencesScreen(name='competences'))
        sm.add_widget(PracticeScreen(name='practice'))
        sm.add_widget(ProgressScreen(name='progress'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        return sm

# Ejecutar la aplicación
if __name__ == '__main__':
    ASMETCBTApp().run()
