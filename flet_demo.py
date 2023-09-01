import flet as ft
import time

from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Container,
    Page,
    Row,
    Text,
    icons,
)


def main(page: Page):
    page.title = "IG Scraper"
    page.window_maximizable = False
    # Pick files dialog
    def pick_files_result(e: FilePickerResultEvent):
        analyze_btn.disabled = True
        file_saver_btn.disabled = True
        selected_files.value = (
            e.files[0].path if e.files else "Please select a file"
        )
        if e.files:
            analyze_btn.disabled = False
        info_text.value = ""
        page.update()

    def save_files_result(e: FilePickerResultEvent):
        if e.path:
            info_text.value += '\nSaving ... '
            page.update()
            time.sleep(1)
            if result_list[0] is not None:
                try:
                    file_path = e.path + '.csv'
                    result_list[0].to_csv(file_path)
                    info_text.value += 'Successful!'
                    info_text.value += f'\nFile saved to {file_path}'
                except Exception as e:
                    info_text.value += 'Failed!'
                    info_text.value += f'\nError: {e}'
            page.update()


    def analyze_click(e):
        progress_ctn.content = progress_bar
        analyze_btn.disabled = True
        file_picker_btn.disabled = True
        file_saver_btn.disabled = True
        info_text.value = 'Retrieving information ... '
        page.update()
        time.sleep(2)
        from ig_dm_scraper.scraper import get_dm_from_zip
        from ig_dm_scraper.formatter import reformat
        from ig_dm_scraper.anonymizer import anonymize
        try:
            raw = get_dm_from_zip(filepath=selected_files.value, oldest_date='2023-05-01')
            info_text.value += 'Done'
            info_text.value += '\nReformatting the data ... '
            page.update()
            df = reformat(raw, as_dataframe=True)
            info_text.value += 'Done'
            info_text.value += '\nAnonymizing the data ... '
            page.update()
            anom_df = anonymize(df)
            info_text.value += 'Done'
            info_text.value += '\nClick save to choose where to save the output.'
            print(anom_df)
            # Save in the storage
            result_list[0] = anom_df
            # Activate file saving button
            file_saver_btn.disabled = False
        except Exception as e:
            print(e)
            info_text.value += f'\nError: {e}'
        progress_ctn.content = None
        file_picker_btn.disabled = False
        analyze_btn.disabled = False
        page.update()


    page.window_resizable = False
    page.window_height = 400
    page.window_width = 400

    pick_files_dialog = FilePicker(on_result=pick_files_result)
    save_files_dialog = FilePicker(on_result=save_files_result)

    analyze_btn = ElevatedButton("ANALYZE", disabled=True,
                                  on_click=analyze_click)

    selected_files = Text(
        'Please select a file', 
        text_align='CENTER',
        overflow='ELLIPSIS'
    )

    info_text = Text(
        '',
        bgcolor=ft.colors.GREY_300
    )
    # hide all dialogs in overlay
    page.overlay.extend([pick_files_dialog, save_files_dialog])

    progress_ctn = Container(
            padding=0,
            width=360,
            height=3,
    )

    # Variable for saving result dataframe
    result_list = [None]

    file_saver_btn = ElevatedButton(
        "SAVE", 
        disabled=True,
        icon=icons.SAVE,
        on_click=lambda _:save_files_dialog.save_file(
            allowed_extensions=['csv']
        )
    )

    file_picker_btn = ElevatedButton(
        "Pick files",
        icon=icons.UPLOAD_FILE,
        on_click=lambda _: pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=['zip']
        ),
    )

    progress_bar = ft.ProgressBar(width=420, color="amber", bgcolor="#eeeeee")

    page.add(
        Row(
            [
                file_picker_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        Container(
            content=selected_files,
            width=380
        ),
        Row(
                [
                    analyze_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER
        ),
        Row(
                [
                    progress_ctn
                ],
                alignment=ft.MainAxisAlignment.CENTER
        ),
        Container(
            content = info_text,
            bgcolor=ft.colors.GREY_300,
            padding=3,
            width=400,
            height=170,
        ),
        Row(
            [
                file_saver_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )


ft.app(target=main)