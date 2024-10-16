import os

import pandas as pd


class PriceMachine:
    def __init__(self):
        self.data = []
        self.name_length = 0

    def load_prices(self, file_path="data"):
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        # Варианты названий столбцов, которые могут содержать информацию о товаре, цене и весе
        name_variants = ["товар", "название", "наименование", "продукт"]
        price_variants = ["цена", "розница"]
        weight_variants = ["вес", "масса", "фасовка"]

        # Перебор файлов в указанном каталоге
        for file_ in os.listdir(file_path):
            # Проверяем, что в названии файла есть "price" и он заканчивается на ".csv"
            if "price" in file_ and file_.endswith(".csv"):
                file_path_full = os.path.join(file_path, file_)
                try:
                    # Загружаем данные из файла CSV в DataFrame
                    df = pd.read_csv(file_path_full, encoding="utf-8")
                    name_col, price_col, weight_col = self._search_product_price_weight(
                        df.to_dict(orient="list").keys(),
                        name_variants,
                        price_variants,
                        weight_variants,
                    )

                    # Проверка, что найденные столбцы не пустые
                    if (
                        name_col is not None
                        and price_col is not None
                        and weight_col is not None
                    ):
                        # Создание DataFrame с необходимыми столбцами и добавление новых полей
                        df_selected = df[[name_col, price_col, weight_col]].copy()
                        df_selected.columns = ["name", "price", "weight"]
                        df_selected["file"] = file_
                        df_selected["price_per_kg"] = (
                            df_selected["price"] / df_selected["weight"]
                        )

                        # Добавляем обработанные данные в список и обновляем максимальную длину названия
                        self.data.append(df_selected)
                        self.name_length = max(
                            self.name_length, df_selected["name"].str.len().max()
                        )
                except Exception as e:
                    # Обработка исключений при чтении файла и добавлении данных
                    print(f"Ошибка при чтении файла {file_}: {e}")

    def _search_product_price_weight(
        self, columns, name_variants, price_variants, weight_variants
    ):
        """Вспомогательная функция для поиска столбцов, соответствующих имени, цене и весу"""
        name_col = next(
            (
                col
                for col in columns
                if any(var in col.lower() for var in name_variants)
            ),
            None,
        )
        price_col = next(
            (
                col
                for col in columns
                if any(var in col.lower() for var in price_variants)
            ),
            None,
        )
        weight_col = next(
            (
                col
                for col in columns
                if any(var in col.lower() for var in weight_variants)
            ),
            None,
        )

        return name_col, price_col, weight_col

    def export_to_html(self, fname="output.html"):
        """Экспортирует собранные данные в HTML-файл"""
        all_data = pd.concat(self.data, ignore_index=True)
        html_content = """
        <html>
        <head>
            <title>Цены</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """

        # Перебор всех строк данных и их добавление в таблицу HTML
        for idx, row in all_data.iterrows():
            html_content += f"""
                <tr>
                    <td>{idx + 1}</td>
                    <td>{row['name']}</td>
                    <td>{row['price']}</td>
                    <td>{row['weight']}</td>
                    <td>{row['file']}</td>
                    <td>{row['price_per_kg']:.2f}</td>
                </tr>
            """

        html_content += """
            </table>
        </body>
        </html>
        """

        # Запись HTML-содержимого в файл
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Данные выгружены в output.html")

    def find_text(self, search_text: str) -> pd.DataFrame:
        """Поиск в загруженных данных по названию товара"""
        all_data = pd.concat(self.data, ignore_index=True)
        filtered_data = all_data[
            all_data["name"].str.contains(search_text, case=False, na=False)
        ]
        filtered_data = filtered_data.copy()
        filtered_data.sort_values(by="price_per_kg", inplace=True, ignore_index=True)
        if filtered_data.empty:
            return "Данных с таким значением не существует"
        return filtered_data


price_machine = PriceMachine()

price_machine.load_prices()
price_machine.export_to_html(fname="output.html")
while True:
    input_ = input("Поиск..")
    if input_ != "exit":
        print(price_machine.find_text(input_))
    else:
        break
