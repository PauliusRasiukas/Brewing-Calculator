import tkinter
import tkinter.messagebox
import customtkinter

import numpy as np
import pandas as pd

from tinydb import TinyDB, Query, where
from PIL import Image

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.database = TinyDB('BeerDatabase.json')
        self.title("Brewing calculator")
        self.grid_columnconfigure((1, 2), weight=1)
        self.grid_columnconfigure(3, weight=7)
        self.grid_rowconfigure((0, 1), weight=1)

        self.og = 0
        self.fg = 0
        self.sum_srm = 0
        self.sum_ibu = 0
        self.toplevel_window = None

        self.green_check = customtkinter.CTkImage(Image.open('raw_files/visual/green_check.webp'),
                                                  size=(20, 20))
        self.arrow_down = customtkinter.CTkImage(Image.open('raw_files/visual/red_arrow_down.png'),
                                                 size=(20, 20))
        self.arrow_up = customtkinter.CTkImage(Image.open('raw_files/visual/red_arrow_up.png'),
                                               size=(20, 20))

        self.description_frame = customtkinter.CTkFrame(self, width=700)
        self.description_frame.grid(row=0, column=0, sticky="nsew")

        (
            customtkinter.CTkLabel(self.description_frame, text="Beer Description",
                                   font=customtkinter.CTkFont(size=15, weight="bold"))
            .grid(row=0, column=0, columnspan=2)
        )

        for idx, lb in enumerate(['Name', 'Style', 'Substyle', '']):
            (
                customtkinter.CTkLabel(self.description_frame, text=lb,
                                       font=customtkinter.CTkFont(size=12, weight="bold"))
                .grid(row=idx * 2 + 1, column=0, padx=20, pady=5)
            )

        self.beer_name = customtkinter.CTkComboBox(self.description_frame,
                                                   values=[beer.get('Name') for beer in
                                                           self.database.table('Recipes').search(
                                                               Query().Name.exists())],
                                                   width=250, command=self.update_recipe)
        self.beer_name.grid(row=1, column=1, padx=20, pady=5)

        self.style = customtkinter.CTkOptionMenu(self.description_frame,
                                                 dynamic_resizing=False,
                                                 values=[style.get('0') for style in
                                                         self.database.table('Styles').search(Query()['0'].exists())],
                                                 width=250, command=self.update_sub_styles)

        self.style.grid(row=3, column=1, padx=20, pady=5)

        self.sub_style = customtkinter.CTkOptionMenu(self.description_frame,
                                                     dynamic_resizing=False,
                                                     width=250, command=self.check_sub_style)
        self.sub_style.grid(row=5, column=1, padx=20, pady=5)

        self.beer_description = []
        self.beer_adjustments = []
        for idx, lb in enumerate(['Target OG: 0', 'Final SG: 0', 'ABV %: 0', 'SRM: 0', 'IBU: 0']):
            label = customtkinter.CTkLabel(self.description_frame, text=lb, anchor="w")
            label.grid(row=1 + idx, column=2, padx=40, pady=5)
            self.beer_description.append(label)
            label2 = customtkinter.CTkLabel(self.description_frame, text='')
            label2.grid(row=1 + idx, column=3)
            self.beer_adjustments.append(label2)

        self.options_frame = customtkinter.CTkFrame(self, width=700)
        self.options_frame.grid(row=0, column=1, sticky="nsew")

        (
            customtkinter.CTkLabel(self.options_frame, text="Brewing setup",
                                   font=customtkinter.CTkFont(size=15, weight="bold"))
            .grid(row=0, column=1, padx=50)
        )

        for idx, lb in enumerate(['ABV (%)', 'Volume (L)', 'Boil time (min)', 'Mash Temp (C)', 'Yeast']):
            (customtkinter.CTkLabel(self.options_frame, text=lb, font=customtkinter.CTkFont(size=12, weight="bold"),
                                    anchor="w")
             .grid(row=1 + idx, column=0, padx=50, pady=5))

        for idx, lb in enumerate(['Mash Volume', 'Sparge Volume']):
            (customtkinter.CTkLabel(self.options_frame, text=lb, font=customtkinter.CTkFont(size=12, weight="bold"),
                                    anchor="w").grid(row=1 + idx, column=2, padx=50, pady=5))

        self.beer_options = []
        for idx in range(4):
            entry = customtkinter.CTkEntry(self.options_frame, width=200)
            entry.grid(row=1 + idx, column=1, padx=40, pady=5, sticky="nsew")
            entry.bind(sequence='<Return>', command=self.calculate)
            self.beer_options.append(entry)

        self.yeast = customtkinter.CTkOptionMenu(self.options_frame,
                                                 dynamic_resizing=False,
                                                 values=[yeast.get('Yeast') for yeast in
                                                         self.database.table('Yeast').search(
                                                             Query().Yeast.exists())],
                                                 width=200, command=self.calculate)
        self.yeast.grid(row=5, column=1, padx=20, pady=5)

        for idx in range(2):
            label = customtkinter.CTkLabel(self.options_frame, text='test', anchor='w')
            label.grid(row=1 + idx, column=3, padx=40, pady=5, sticky="ns")
            self.beer_options.append(label)

        self.malt_frame = customtkinter.CTkFrame(self, width=700)
        self.malt_frame.grid(row=1, column=0, sticky="nsew")

        for idx, title in enumerate(['Malts', 'Malt Ratio (%)', 'SRM', 'Weight']):
            (customtkinter.CTkLabel(self.malt_frame, text=title,
                                    font=customtkinter.CTkFont(size=12, weight="bold"))
             .grid(row=0, column=idx, padx=20))

        self.malts = []
        malt_values = [malt.get('Name') for malt in self.database.table('Malts').search(Query().Name.exists())]
        malt_values.append('NaN')
        for idx in range(8):
            entry = customtkinter.CTkOptionMenu(self.malt_frame, values=malt_values, command=self.calculate, width=200)
            entry.grid(row=1 + idx, column=0, padx=40, pady=5, sticky="nsew")
            self.malts.append(entry)

        self.malt_ratios = []
        for idx in range(8):
            entry = customtkinter.CTkEntry(self.malt_frame)
            entry.grid(row=1 + idx, column=1, padx=40, pady=5, sticky="nsew")
            entry.bind(sequence='<Return>', command=self.calculate)
            self.malt_ratios.append(entry)

        self.srm = []
        for idx in range(8):
            entry = customtkinter.CTkLabel(self.malt_frame, text='0')
            entry.grid(row=1 + idx, column=2, padx=40, pady=5, sticky="nsew")
            self.srm.append(entry)

        self.weights = []
        for idx in range(8):
            entry = customtkinter.CTkLabel(self.malt_frame, text='0 kg')
            entry.grid(row=1 + idx, column=3, padx=40, pady=5, sticky="nsew")
            self.weights.append(entry)

        self.malt_totals = []
        for idx, lb in enumerate(['Total:', '0%', '0', '0 kg']):
            entry = customtkinter.CTkLabel(self.malt_frame, text=lb, font=customtkinter.CTkFont(size=12, weight="bold"))
            entry.grid(row=9, column=idx, padx=40, pady=5, sticky="nsew")
            self.malt_totals.append(entry)

        self.hops_frame = customtkinter.CTkFrame(self, width=700)
        self.hops_frame.grid(row=1, column=1, sticky="nsew")

        for idx, title in enumerate(['Hops', 'Hop Amount (g)', 'Addition (min)', 'IBU']):
            (customtkinter.CTkLabel(self.hops_frame, text=title,
                                    font=customtkinter.CTkFont(size=12, weight="bold"))
             .grid(row=0, column=idx, padx=20))

        self.hops = []
        hop_values = [hop.get('Name') for hop in self.database.table('Hops').search(Query().Name.exists())]
        hop_values.append('NaN')
        for idx in range(8):
            entry = customtkinter.CTkOptionMenu(self.hops_frame, values=hop_values, command=self.calculate, width=150)
            entry.grid(row=1 + idx, column=0, padx=40, pady=5, sticky="nsew")
            self.hops.append(entry)

        self.hop_amounts = []
        for idx in range(8):
            entry = customtkinter.CTkEntry(self.hops_frame)
            entry.grid(row=1 + idx, column=1, padx=40, pady=5, sticky="nsew")
            entry.bind(sequence='<Return>', command=self.calculate)
            self.hop_amounts.append(entry)

        self.hop_additions = []
        for idx in range(8):
            entry = customtkinter.CTkEntry(self.hops_frame)
            entry.grid(row=1 + idx, column=2, padx=40, pady=5, sticky="nsew")
            entry.bind(sequence='<Return>', command=self.calculate)
            self.hop_additions.append(entry)

        self.ibu = []
        for idx in range(8):
            entry = customtkinter.CTkLabel(self.hops_frame, text='0')
            entry.grid(row=1 + idx, column=3, padx=40, pady=5, sticky="nsew")
            self.ibu.append(entry)

        self.hops_totals = []
        for idx, lb in enumerate(['0g', '0']):
            entry = customtkinter.CTkLabel(self.hops_frame, text=lb, font=customtkinter.CTkFont(size=12, weight="bold"))
            entry.grid(row=9, column=idx * 2 + 1, padx=40, pady=5, sticky="nsew")
            self.hops_totals.append(entry)

        self.color_frame = customtkinter.CTkFrame(self, fg_color='#DE7C00', width=100)
        self.color_frame.grid(row=0, column=2, sticky="nsew")

        self.color_name = customtkinter.CTkLabel(self.color_frame, text="Beer Color", text_color='black',
                                                 font=customtkinter.CTkFont(size=15, weight="bold"))
        self.color_name.grid(row=0, column=0, sticky='ns', padx=5)

        self.button_frame = customtkinter.CTkFrame(self, width=100)
        self.button_frame.grid(row=1, column=2, sticky="nsew")
        self.save_button = customtkinter.CTkButton(self.button_frame, text="Save Recipe", height=50,
                                                   command=self.save_recipe).grid(row=0, column=0, pady=10, padx=5)
        self.delete_button = customtkinter.CTkButton(self.button_frame, text="Delete Recipe", height=50,
                                                     command=self.delete_recipe).grid(row=1, column=0, padx=5)

        self.update_button = customtkinter.CTkButton(self.button_frame, text="Update Database", height=50,
                                                     command=self.read_tables_to_database).grid(row=2, column=0, pady=100, padx=5)

        self.update_recipe(self.beer_name.get())
        self.calculate(0)

    def calculate(self, event):
        abv = float(self.beer_options[0].get())
        yeast = self.database.table('Yeast').search(Query().Yeast == self.yeast.get())[0]
        f_factor = self.database.table('F-factor').search(
            (Query()['ABV (min)'] <= abv) & (Query()['ABV (max)'] >= abv))[0]['f-factor']
        mash_efficiency = 0.8
        mash_dead_space_liters = 3.5
        boiler_loses = 5

        dextrin_level = yeast[self.beer_options[3].get()]
        deg_gravity_required = abv / f_factor / (1 - float(dextrin_level))
        self.og = 1000 + deg_gravity_required
        self.fg = (self.og - 1000) * float(dextrin_level) + 1000

        target_extract = deg_gravity_required * float(self.beer_options[1].get()) / mash_efficiency

        try:
            sum_kg = 0
            sum_ratio = 0
            self.sum_srm = 0
            volume = float(self.beer_options[1].get())
            for idx, (grain, ratio) in enumerate(zip(self.malts, self.malt_ratios)):
                grain_extract = self.database.table('Malts').search(Query().Name == grain.get())[0]
                grain_weight = np.round(target_extract * float(ratio.get()) / float(grain_extract['Extraction']), 1)
                self.weights[idx].configure(text=f'{str(grain_weight)} kg')
                sum_kg += grain_weight

                srm = ((float(grain_extract['Colour']) * grain_weight * 2.20462 / (
                        volume * 0.219969)) ** 0.6859) * 1.4922
                self.srm[idx].configure(text=f'{str(np.round(srm, 1))}')
                self.sum_srm += srm
                sum_ratio += float(ratio.get())

        except IndexError:
            self.malt_totals[3].configure(text=f'{np.round(sum_kg, 1)} kg')
            self.malt_totals[2].configure(text=f'{np.round(self.sum_srm, 1)}')
            self.malt_totals[1].configure(text=f'{np.round(sum_ratio, 2)}')

            srm_hex = self.database.table('Colors').search(Query().SRM == np.round(max(1, min(40, self.sum_srm))))[0]
            self.color_frame.configure(fg_color=srm_hex['Hex'])
            if np.round(max(1, min(40, self.sum_srm))) < 20:
                self.color_name.configure(text_color='black')
            else:
                self.color_name.configure(text_color='white')

            self.beer_options[4].configure(text=f'{np.round(sum_kg * 2.7) + mash_dead_space_liters} L')
            self.beer_options[5].configure(
                text=f'{np.round(volume + boiler_loses - (sum_kg * 2.7 + mash_dead_space_liters) + (sum_kg * 0.8))} L')

        try:
            sum_hops = 0
            self.sum_ibu = 0
            for idx, (hop, amount, time) in enumerate(zip(self.hops, self.hop_amounts, self.hop_additions)):
                hop_extract = self.database.table('Hops').search(Query().Name == hop.get())[0]
                sum_hops += float(amount.get())

                try:
                    utilisation_upper = self.database.table('Util').search(Query().Gravity >= (self.og / 1000))[0][
                        time.get()]
                    utilisation_lower = self.database.table('Util').search(Query().Gravity <= (self.og / 1000))[-1][
                        time.get()]
                except KeyError:
                    utilisation_upper = 0
                    utilisation_lower = 0

                interpolation_factor = (self.database.table('Util').search(Query().Gravity >= (self.og / 1000))[0][
                                            'Gravity']
                                        - (self.og / 1000)) / 0.01
                utilisation = utilisation_upper + interpolation_factor * (utilisation_lower - utilisation_upper)
                ibu = float(hop_extract['Alpha']) * float(amount.get()) * utilisation / volume * 10
                self.ibu[idx].configure(text=f'{str(np.round(ibu, 1))}')
                self.sum_ibu += ibu

        except IndexError:
            self.hops_totals[0].configure(text=f'{np.round(sum_hops, 0)} g')
            self.hops_totals[1].configure(text=f'{np.round(self.sum_ibu, 1)}')

        self.beer_description[0].configure(text=f'Target OG: {int(self.og)}     ')
        self.beer_description[1].configure(text=f'Final FG: {int((self.og - 1000) * float(dextrin_level) + 1000)}     ')
        self.beer_description[2].configure(text=f'ABV %: {float(self.beer_options[0].get())}     ')
        self.beer_description[3].configure(text=f'SRM: {np.round(self.sum_srm, 1)}     ')
        self.beer_description[4].configure(text=f'IBU: {np.round(self.sum_ibu, 1)}     ')

        self.check_sub_style(self.sub_style.get())

    def check_sub_style(self, sub_style):
        try:
            guide = self.database.table('Styles_guidelines').search(Query()['Style name'] == sub_style)[0]
            targets = ['OG', 'FG', 'ABV', 'SRM', 'IBU']
            values = [self.og, self.fg, self.beer_options[0].get(), self.sum_srm, self.sum_ibu]

            for idx, (target, value) in enumerate(zip(targets, values)):
                if float(guide[f'{target} min']) <= float(value) <= float(guide[f'{target} max']):
                    self.beer_description[idx].configure(image=self.green_check, compound='right')
                    self.beer_adjustments[idx].configure(text='')
                elif float(guide[f'{target} min']) > float(value):
                    self.beer_description[idx].configure(image=self.arrow_up, compound='right')
                    self.beer_adjustments[idx].configure(
                        text=str(np.round(float(guide[f'{target} min']) - float(value), 1)))
                else:
                    self.beer_description[idx].configure(image=self.arrow_down, compound='right')
                    self.beer_adjustments[idx].configure(
                        text=str(np.round(float(value) - float(guide[f'{target} max']), 1)))
        except IndexError:
            pass

    def update_sub_styles(self, current_style):
        sub_style_db = list(self.database.table('Styles')
                            .search(Query()['0'] == current_style))
        if sub_style_db:
            sub_style_list = list(map(str, sub_style_db[0].values()))[1::]
            while 'nan' in sub_style_list:
                sub_style_list.remove('nan')

            self.sub_style.configure(values=sub_style_list)
            self.sub_style.set(sub_style_list[0])
        else:
            self.sub_style.configure(values=['NaN'])
            self.sub_style.set('NaN')

    def update_recipe(self, beer_name):
        recipe = self.database.table('Recipes').search(Query().Name == beer_name)[0]
        self.style.set(recipe['Style'])
        self.update_sub_styles(recipe['Style'])

        option_labels = ['ABV', 'Liters', 'Boil time (min)', 'Mash Temp (oC)']
        for idx, lb in enumerate(option_labels):
            self.beer_options[idx].delete(0, tkinter.END)
            self.beer_options[idx].insert(0, recipe[lb])

        self.yeast.set(recipe['Yeast'])

        for idx in range(8):
            self.malts[idx].set(recipe[f'Malt name {idx}'])

            self.hops[idx].set(recipe[f'Hop name {idx}'])

            self.malt_ratios[idx].delete(0, tkinter.END)
            self.malt_ratios[idx].insert(0, recipe[f'Malt Ratio {idx}'])

            self.hop_amounts[idx].delete(0, tkinter.END)
            self.hop_amounts[idx].insert(0, recipe[f'Hop amount {idx}'])

            self.hop_additions[idx].delete(0, tkinter.END)
            self.hop_additions[idx].insert(0, recipe[f'Hop Time {idx}'])

        self.calculate(0)

    def update_raw_csv(self):
        pd.DataFrame(self.database.table('Recipes').all()).to_csv('raw_files/tables/Recipes.csv')

    def read_tables_to_database(self):
        all_dicts = []
        recipes = pd.read_csv('raw_files/tables/Recipes.csv').transpose()
        all_dicts.append(recipes.to_dict())

        beer_styles = pd.read_csv('raw_files/tables/style_guidelines.csv', index_col=0)
        all_dicts.append(beer_styles.to_dict())

        style_table = pd.read_csv('raw_files/tables/styles.csv', header=None)
        all_dicts.append(style_table.to_dict())

        yeast_table = pd.read_csv('raw_files/tables/yeast_profile.csv', header=None, index_col=0)
        all_dicts.append(yeast_table.to_dict())

        malt_table = pd.read_csv('raw_files/tables/malt_list.csv', header=None, index_col=0)
        all_dicts.append(malt_table.to_dict())

        hops_table = pd.read_csv('raw_files/tables/hops_list.csv', header=None, index_col=0)
        all_dicts.append(hops_table.to_dict())

        f_factor_table = pd.read_csv('raw_files/tables/f-factor.csv').transpose()
        all_dicts.append(f_factor_table.to_dict())

        color_table = pd.read_csv('raw_files/tables/colors.csv').transpose()
        all_dicts.append(color_table.to_dict())

        utilization_table = pd.read_csv('raw_files/tables/utilization_table.csv', header=None, index_col=0)
        all_dicts.append(utilization_table.to_dict())

        self.database = TinyDB('BeerDatabase.json')

        for t in self.database.tables():
            self.database.table(t).truncate()

        all_tables = ['Recipes', 'Styles_guidelines', 'Styles', 'Yeast', 'Malts', 'Hops', 'F-factor', 'Colors', 'Util']
        for one_table, one_dicts in zip(all_tables, all_dicts):
            self.database.table(one_table).insert_multiple([x[1] for x in one_dicts.items()])

        beer_list = [beer.get('Name') for beer in
                     self.database.table('Recipes').search(
                         Query().Name.exists())]
        self.beer_name.configure(values=beer_list)
        hop_values = [hop.get('Name') for hop in self.database.table('Hops').search(Query().Name.exists())]
        hop_values.append('NaN')
        malt_values = [hop.get('Name') for hop in self.database.table('Malts').search(Query().Name.exists())]
        malt_values.append('NaN')
        for idx in range(8):
            self.hops[idx].configure(values=hop_values)
            self.malts[idx].configure(values=malt_values)

        self.beer_name.set(beer_list[0])
        self.update_recipe(beer_list[0])

    def delete_recipe(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.flag = 'Delete'
            self.execute = self.delete_recipe_db
            self.toplevel_window = Confirmation(self)
            self.toplevel_window.title('Deletion confirmation')
            self.toplevel_window.after(10, lambda: self.toplevel_window.focus_force())
        else:
            self.toplevel_window.focus()  # if window exists focus it

    def save_recipe(self):
        beer_list = [beer.get('Name') for beer in
                     self.database.table('Recipes').search(
                         Query().Name.exists())]
        if self.beer_name.get() in beer_list:
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.flag = 'Overwrite'
                self.execute = self.save_recipe_db
                self.toplevel_window = Confirmation(self)
                self.toplevel_window.title('Overwrite confirmation')
                self.toplevel_window.after(10, lambda: self.toplevel_window.focus_force())
            else:
                self.toplevel_window.focus()  # if window exists focus it
        else:
            self.database.table('Recipes').upsert(self.dict_to_load(), Query().name == 'Nothing')
            beer_list = [beer.get('Name') for beer in
                         self.database.table('Recipes').search(
                             Query().Name.exists())]
            self.beer_name.configure(values=beer_list)

    def dict_to_load(self):
        dict_to_save = {'Name': self.beer_name.get(), 'Style': self.style.get(), 'Sub Style': self.sub_style.get(),
                        'ABV': self.beer_options[0].get(), 'Liters': self.beer_options[1].get(),
                        'Boil time (min)': self.beer_options[2].get(), 'Mash Temp (oC)': self.beer_options[3].get(),
                        'Yeast': self.yeast.get()}

        for idx in range(8):
            dict_to_save[f'Malt name {idx}'] = self.malts[idx].get()
            dict_to_save[f'Malt Ratio {idx}'] = self.malt_ratios[idx].get()
            dict_to_save[f'Hop name {idx}'] = self.hops[idx].get()
            dict_to_save[f'Hop amount {idx}'] = self.hop_amounts[idx].get()
            dict_to_save[f'Hop Time {idx}'] = self.hop_additions[idx].get()

        return dict_to_save

    def delete_recipe_db(self):
        self.database.table('Recipes').remove(where('Name') == self.beer_name.get())
        beer_list = [beer.get('Name') for beer in
                     self.database.table('Recipes').search(
                         Query().Name.exists())]
        self.beer_name.configure(values=beer_list)
        self.beer_name.set(beer_list[0])
        self.update_recipe(beer_list[0])
        self.update_raw_csv()
        self.close()

    def save_recipe_db(self):
        self.database.table('Recipes').upsert(self.dict_to_load(), Query().Name == self.beer_name.get())
        beer_list = [beer.get('Name') for beer in
                     self.database.table('Recipes').search(
                         Query().Name.exists())]
        self.beer_name.configure(values=beer_list)
        self.update_raw_csv()
        self.close()

    def close(self):
        self.toplevel_window.destroy()


class Confirmation(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = customtkinter.CTkLabel(self, text=f"{self.master.flag} {self.master.beer_name.get()} recipe?")
        self.label.pack(padx=20, pady=20)
        self.save_button = customtkinter.CTkButton(self, text="Yes", height=50, command=self.master.execute).pack(
            padx=20, pady=20)

        self.save_button = customtkinter.CTkButton(self, text="No", height=50, command=self.master.close).pack(padx=20,
                                                                                                        pady=20)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (400 / 2)
        y = (screen_height / 2) - (300 / 2)
        self.geometry('%dx%d+%d+%d' % (400, 300, x, y))


if __name__ == "__main__":
    app = App()
    app.mainloop()
