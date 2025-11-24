import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QProgressBar, QMessageBox, QTabWidget,
                             QSlider, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class InvestmentInstrument:
    """Класс для инвестиционного инструмента"""

    def __init__(self, name, color, base_return, volatility):
        self.name = name
        self.color = color
        self.base_return = base_return
        self.volatility = volatility

    def calculate_return(self, market_impact=0.0):
        """Рассчитываем случайную доходность"""
        random_factor = random.uniform(-self.volatility, self.volatility)
        return self.base_return + random_factor + market_impact


class MarketEvent:
    """Класс для рыночного события, которое ВЛИЯЕТ на доходность"""

    def __init__(self, name, description, impacts):
        self.name = name
        self.description = description
        self.impacts = impacts  # Словарь: {'тип инструмента': влияние}


class InvestmentSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🎮 Инвестиционный симулятор "Расти с ВТБ"')
        self.setFixedSize(1100, 750)

        # Игровые параметры
        self.initial_capital = 10000
        self.current_capital = self.initial_capital
        self.current_week = 1
        self.total_weeks = 12

        # Создаем инструменты
        self.instruments = [
            InvestmentInstrument("💰 Вклад", "#FF6B6B", 0.005, 0.001),
            InvestmentInstrument("📊 Облигации", "#4ECDC4", 0.008, 0.005),
            InvestmentInstrument("📈 Акции", "#45B7D1", 0.012, 0.03),
            InvestmentInstrument("🚀 Рост", "#96CEB4", 0.02, 0.08)
        ]

        # Создаем события, которые ВЛИЯЮТ на доходность
        self.market_events = [
            MarketEvent(
                "📈 Бум на рынке акций",
                "Акции компаний показывают рекордный рост!",
                {"📈 Акции": 0.08, "🚀 Рост": 0.12, "📊 Облигации": -0.02}
            ),
            MarketEvent(
                "📉 Коррекция рынка",
                "Рынок акций переживает временное снижение",
                {"📈 Акции": -0.06, "🚀 Рост": -0.10, "💰 Вклад": 0.01}
            ),
            MarketEvent(
                "🎉 Выплата дивидендов",
                "Компании выплатили щедрые дивиденды акционерам",
                {"📈 Акции": 0.04, "🚀 Рост": 0.03}
            ),
            MarketEvent(
                "🏦 Повышение ставки ЦБ",
                "Центробанк повысил ключевую ставку",
                {"💰 Вклад": 0.02, "📊 Облигации": -0.03, "📈 Акции": -0.04}
            ),
            MarketEvent(
                "🌍 Стабильность на рынках",
                "Рынки демонстрируют стабильное развитие",
                {"📈 Акции": 0.02, "📊 Облигации": 0.01}
            ),
            MarketEvent(
                "⚡ Технологический прорыв",
                "IT-компании представили революционные продукты",
                {"🚀 Рост": 0.15, "📈 Акции": 0.05}
            ),
            MarketEvent(
                "💸 Инфляция выше ожиданий",
                "Уровень инфляции превысил прогнозы аналитиков",
                {"💰 Вклад": -0.01, "📊 Облигации": -0.02, "📈 Акции": 0.03}
            )
        ]

        # Начальное распределение
        self.portfolio = {instrument: 0.25 for instrument in self.instruments}

        # История для графиков
        self.capital_history = [self.initial_capital]
        self.week_history = [0]
        self.current_event = None

        self.init_ui()
        self.update_display()

    def init_ui(self):
        """Создаем красивый интерфейс"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # === ШАПКА ===
        header = QLabel('🎯 ИНВЕСТИЦИОННЫЙ СИМУЛЯТОР "РАСТИ С ВТБ"')
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                      stop:0 #0033A0, stop:0.5 #0048CC, stop:1 #0066FF);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 5px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # === ВКЛАДКИ ===
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка 1: Управление портфелем
        self.setup_portfolio_tab()
        # Вкладка 2: Аналитика
        self.setup_analytics_tab()

        # === ПАНЕЛЬ СТАТУСА ===
        self.setup_status_bar(layout)

        # === КНОПКА ХОДА ===
        self.next_button = QPushButton("🎲 СЛЕДУЮЩАЯ НЕДЕЛЯ")
        self.next_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.next_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #FF6B6B, stop:0.5 #4ECDC4, stop:1 #45B7D1);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                margin: 10px;
            }
            QPushButton:hover { background: #0033A0; }
        """)
        self.next_button.clicked.connect(self.next_week)
        layout.addWidget(self.next_button)

    def setup_portfolio_tab(self):
        """Вкладка управления портфелем"""
        tab = QWidget()
        self.tabs.addTab(tab, "🎯 УПРАВЛЕНИЕ")
        layout = QVBoxLayout(tab)

        # Информация о событии
        self.event_label = QLabel("🎪 Добро пожаловать! Распределите портфель и начинайте инвестировать!")
        self.event_label.setStyleSheet("""
            background: #FFF9C4;
            color: #5D4037;
            padding: 12px;
            border: 2px dashed #FFD54F;
            border-radius: 8px;
            font-size: 13px;
        """)
        self.event_label.setWordWrap(True)
        layout.addWidget(self.event_label)

        # === СЛАЙДЕРЫ ДЛЯ УПРАВЛЕНИЯ ===
        layout.addWidget(QLabel("🎛️ РАСПРЕДЕЛЕНИЕ ПОРТФЕЛЯ (%):"))

        self.sliders = {}
        for instrument in self.instruments:
            row = QWidget()
            row_layout = QHBoxLayout(row)

            # Название инструмента
            name_label = QLabel(f"● {instrument.name}")
            name_label.setStyleSheet(f"color: {instrument.color}; font-weight: bold;")
            name_label.setFixedWidth(100)

            # Слайдер
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(25)
            slider.valueChanged.connect(self.update_portfolio_from_sliders)

            # Поле ввода
            input_field = QLineEdit()
            input_field.setFixedWidth(40)
            input_field.setText("25")
            input_field.textChanged.connect(lambda text, inst=instrument: self.update_from_input(text, inst))

            row_layout.addWidget(name_label)
            row_layout.addWidget(slider)
            row_layout.addWidget(QLabel("%"))
            row_layout.addWidget(input_field)

            self.sliders[instrument] = (slider, input_field)
            layout.addWidget(row)

        # Кнопки управления
        button_layout = QHBoxLayout()

        random_btn = QPushButton("🎲 Случайно")
        random_btn.setStyleSheet("background: #BA68C8; color: white; border-radius: 6px; padding: 8px;")
        random_btn.clicked.connect(self.randomize_portfolio)

        reset_btn = QPushButton("🔄 Сбросить")
        reset_btn.setStyleSheet("background: #FF9800; color: white; border-radius: 6px; padding: 8px;")
        reset_btn.clicked.connect(self.reset_portfolio)

        button_layout.addWidget(random_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)

        # Информация о распределении
        self.distribution_label = QLabel()
        self.update_distribution_label()
        layout.addWidget(self.distribution_label)

    def setup_analytics_tab(self):
        """Вкладка с аналитикой"""
        tab = QWidget()
        self.tabs.addTab(tab, "📊 АНАЛИТИКА")
        layout = QVBoxLayout(tab)

        # График matplotlib
        layout.addWidget(QLabel("📈 ДИНАМИКА КАПИТАЛА:"))

        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            background: #E3F2FD;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
        """)
        layout.addWidget(self.stats_label)

    def setup_status_bar(self, layout):
        """Панель статуса"""
        status = QWidget()
        status_layout = QHBoxLayout(status)

        # Текущая неделя
        self.week_label = QLabel("🕐 НЕДЕЛЯ: 1/12")
        self.week_label.setStyleSheet("color: #D32F2F; font-weight: bold;")

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_weeks)
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0033A0;
                border-radius: 8px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: #4ECDC4;
                border-radius: 6px;
            }
        """)

        # Капитал
        self.capital_label = QLabel(f"💰 КАПИТАЛ: {self.current_capital:,.0f} ₽")
        self.capital_label.setStyleSheet("color: #388E3C; font-weight: bold;")

        status_layout.addWidget(self.week_label)
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.capital_label)

        layout.addWidget(status)

    def update_portfolio_from_sliders(self):
        """Обновляем портфель из слайдеров"""
        total = sum(slider.value() for slider, _ in self.sliders.values())

        if total > 0:
            for instrument, (slider, input_field) in self.sliders.items():
                share = slider.value() / total
                self.portfolio[instrument] = share
                input_field.blockSignals(True)
                input_field.setText(str(slider.value()))
                input_field.blockSignals(False)

        self.update_distribution_label()

    def update_from_input(self, text, instrument):
        """Обновляем из поля ввода"""
        try:
            value = int(text) if text else 0
            value = max(0, min(100, value))

            slider, input_field = self.sliders[instrument]
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)

            self.update_portfolio_from_sliders()
        except ValueError:
            pass

    def randomize_portfolio(self):
        """Случайное распределение"""
        shares = [random.randint(5, 80) for _ in self.instruments]
        total = sum(shares)

        for i, instrument in enumerate(self.instruments):
            slider, input_field = self.sliders[instrument]
            value = int((shares[i] / total) * 100)
            slider.setValue(value)

        QMessageBox.information(self, "🎲", "Портфель перераспределен!")

    def reset_portfolio(self):
        """Сброс к равному распределению"""
        share_percent = int(100 / len(self.instruments))
        for instrument in self.instruments:
            slider, input_field = self.sliders[instrument]
            slider.setValue(share_percent)

    def update_distribution_label(self):
        """Обновляем информацию о распределении"""
        text = "📊 ТЕКУЩЕЕ РАСПРЕДЕЛЕНИЕ: "
        distribution = []
        for instrument, share in self.portfolio.items():
            percent = share * 100
            distribution.append(f"{instrument.name}: {percent:.1f}%")

        text += " | ".join(distribution)
        self.distribution_label.setText(text)
        self.distribution_label.setStyleSheet("background: #E8F5E8; padding: 6px; border-radius: 5px;")

    def update_display(self):
        """Обновляем весь интерфейс"""
        self.week_label.setText(f"🕐 НЕДЕЛЯ: {self.current_week}/{self.total_weeks}")
        self.progress_bar.setValue(self.current_week)
        self.capital_label.setText(f"💰 КАПИТАЛ: {self.current_capital:,.0f} ₽")
        self.update_chart()
        self.update_stats()

    def update_chart(self):
        """Обновляем график matplotlib"""
        self.ax.clear()

        self.ax.plot(self.week_history, self.capital_history,
                     color='#0033A0', linewidth=3, marker='o', markersize=6,
                     markerfacecolor='#FF6B6B', markeredgecolor='white', markeredgewidth=2)

        self.ax.set_facecolor('#F8F9FA')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('Недели', fontsize=12)
        self.ax.set_ylabel('Капитал (руб)', fontsize=12)
        self.ax.set_title('📈 Рост вашего капитала', fontsize=14, fontweight='bold', color='#0033A0')

        self.ax.tick_params(axis='both', which='major', labelsize=10)

        self.canvas.draw()

    def update_stats(self):
        """Обновляем статистику"""
        if len(self.capital_history) > 1:
            total_return = (self.current_capital - self.initial_capital) / self.initial_capital * 100

            text = f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 15px; border-radius: 8px;'>
                <h3 style='margin: 0;'>📊 ВАША СТАТИСТИКА:</h3>
                <p>🏁 Начальный капитал: <b>{self.initial_capital:,.0f} ₽</b></p>
                <p>💰 Текущий капитал: <b>{self.current_capital:,.0f} ₽</b></p>
                <p>🎯 Общая доходность: <b>{total_return:+.1f}%</b></p>
            </div>
            """
            self.stats_label.setText(text)

    def next_week(self):
        """Следующий ход"""
        if self.current_week > self.total_weeks:
            QMessageBox.information(self, "🎉", "Игра завершена! Смотрите результаты в Аналитике!")
            return

        # Выбираем случайное событие, которое ВЛИЯЕТ на доходность
        self.current_event = random.choice(self.market_events)

        # Рассчитываем доходность с учетом события
        old_capital = self.current_capital
        total_return = 0.0

        for instrument, share in self.portfolio.items():
            # Получаем влияние события на этот инструмент (если есть)
            event_impact = self.current_event.impacts.get(instrument.name, 0.0)
            # Рассчитываем доходность инструмента с учетом события
            instrument_return = instrument.calculate_return(event_impact)
            total_return += share * instrument_return

        # Обновляем капитал
        self.current_capital *= (1 + total_return)
        self.current_capital = max(0, self.current_capital)

        # Сохраняем историю
        self.capital_history.append(self.current_capital)
        self.week_history.append(self.current_week)

        # Показываем результат недели с УЧЕТОМ СОБЫТИЯ
        week_return = (self.current_capital - old_capital) / old_capital * 100

        # Цвет события в зависимости от влияния
        event_color = "#4CAF50" if week_return > 0 else "#F44336"

        event_text = f"""
        <div style='background: {event_color}; color: white; padding: 10px; border-radius: 8px;'>
            <b>🎪 НЕДЕЛЯ {self.current_week}: {self.current_event.name}</b><br>
            {self.current_event.description}<br>
            📈 Доходность недели: <b>{week_return:+.1f}%</b>
        </div>
        """
        self.event_label.setText(event_text)

        # Переходим к следующей неделе
        self.current_week += 1

        # Конец игры?
        if self.current_week > self.total_weeks:
            self.finish_game()
        else:
            self.update_display()

    def finish_game(self):
        """Завершаем игру"""
        self.next_button.setEnabled(False)
        self.next_button.setText("🎮 ИГРА ЗАВЕРШЕНА")

        total_return = (self.current_capital - self.initial_capital) / self.initial_capital * 100

        # Результат
        if total_return > 20:
            message = "🎉 ВЫ ГЕНИЙ ИНВЕСТИЦИЙ! Отличный результат!"
        elif total_return > 5:
            message = "👍 ХОРОШАЯ РАБОТА! Ваш капитал вырос!"
        elif total_return > -5:
            message = "👉 НЕПЛОХО! Вы сохранили капитал."
        else:
            message = "💪 НЕ УНЫВАЙТЕ! Попробуйте еще раз!"

        QMessageBox.information(self, "🏁 ИГРА ЗАВЕРШЕНА",
                                f"{message}\n\n"
                                f"Ваш результат: {total_return:+.1f}%\n"
                                f"Начальный капитал: {self.initial_capital:,.0f} ₽\n"
                                f"Финальный капитал: {self.current_capital:,.0f} ₽")

        self.tabs.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                      stop:0 #E3F2FD, stop:0.5 #F3E5F5, stop:1 #E8F5E8);
        }
        QWidget {
            font-family: Arial;
        }
    """)

    game = InvestmentSimulator()
    game.show()

    sys.exit(app.exec_())