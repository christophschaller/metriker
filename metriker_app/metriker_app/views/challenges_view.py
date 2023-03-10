from dataclasses import dataclass

import flet as ft

from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
from flet.plotly_chart import PlotlyChart

from .base_view import BaseView


@dataclass
class Challenge:
    name: str
    icon: str
    content: ft.Control


# vari=ft.Text("run")
CHALLENGES = {
    "bike": Challenge(name="bike", icon=ft.icons.PEDAL_BIKE, content=ft.Container(content=ft.Text("Bike"))),
    "run": Challenge(name="run", icon=ft.icons.HIKING, content=ft.Container(content=ft.Text("run"))),
}


class ChallengeContent(ft.Column):
    def __init__(self, app, sport_type, start_date, end_date, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.sport_type = sport_type
        self.start_date = start_date
        self.end_date = end_date

        self.controls = [
            ft.Container(self.create_chart()),
            ft.Container(self.create_table()),
        ]

    def get_table_rows(self):  # sport="Ride" e.g.
        user_distance = []
        for user in self.app.user_handler.values():
            distance = sum(
                [
                    activity.distance
                    for activity in self.app.activity_handler.get_user_activities(
                        user.id,
                        sport_type=self.sport_type,
                        start_date="2023-01-01 00:02:00",
                        end_date="2023-01-02 00:001:00",
                    )
                ]
            )
            user_distance.append((user, distance))

        sorted_user_distance = sorted(user_distance, key=lambda x: x[1], reverse=True)

        rows = []
        for i, elem in enumerate(sorted_user_distance):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataColumn(ft.Text(i + 1)),
                        ft.DataCell(
                            # ft.Text(elem[0].name),
                            ft.TextButton(
                                text=elem[0].name,
                                data=elem[0].id,
                                on_click=lambda e: self.app.page.go(f"/user/{e.control.data}"),
                            )
                            # on_tap=lambda e: self.app.page.go(f"/user/{elem[0].id}"),
                        ),  # TODO: find better way to link users
                        ft.DataCell(ft.Text(elem[1])),
                    ],
                ),
            )
        return rows

    def get_sport_plot(self, start_date, end_date):
        start_date = datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")

        all_activities = []
        for user in self.app.user_handler.values():
            month_list = []
            for month in range(end_date.month - start_date.month + 1):
                month_list.append(start_date.month + month)

            user_activities = []
            for month in month_list:
                new_start_date = datetime(2023, month, 1, 0, 0, 0)
                new_end_date = datetime(2023, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

                month_distance = sum(
                    [
                        activity.distance
                        for activity in self.app.activity_handler.get_user_activities(
                            user.id,
                            sport_type=self.sport_type,
                            start_date=new_start_date,
                            end_date=new_end_date,
                        )
                    ]
                )
                # month_distance = (month,month_distance)
                user_activities.append(month_distance)
            all_activities.append(user_activities)
            # print("###### user_activities = "+str(user_activities))

        # month_columns = []
        # usernames_index = []
        df = pd.DataFrame(all_activities)  # ,columns=month_columns, index=usernames_index)
        # print(df)

        # sport_graph = PlotlyChart(px.line(df#.transpose()
        #                                  ))#,template="simple_white", line_shape="spline",labels={'value':'Kilometer', 'index':'Monate'}))#, expand=True)
        return df  # sport_graph

    def create_chart(self):
        return PlotlyChart(
            px.line(self.get_sport_plot("2023-01-01 00:00:05", "2023-03-03 00:00:05").transpose())
        )  # ,template="simple_white", line_shape="spline",labels={'value':'Kilometer', 'index':'Monate'}))#, expand=True)# self._active_content

    def create_table(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Place"), numeric=True),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Distance"), numeric=True),
            ],
            rows=self.get_table_rows(),
        )


class ChallengesView(BaseView):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/challenges"

        # TODO: find proper place for challenge configuration
        self.challenges = {
            "bike": Challenge(
                name="bike",
                icon=ft.icons.PEDAL_BIKE,
                content=ChallengeContent(self.app, "bike", "2023-01-01 00:00:01", "2023-03-03 00:00:05"),
            ),
            "run": Challenge(
                name="run",
                icon=ft.icons.HIKING,
                content=ChallengeContent(self.app, "run", "2023-01-01 00:00:01", "2023-03-03 00:00:05"),
            ),
        }
        self.nav_bar = self.create_nav_bar()
        self._active_content = ft.Container()
        self.padding = ft.padding.all(100)

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        self.controls.extend([self.nav_bar, self._active_content])

    def set_active_challenge(self, name: str):
        self._active_content = self.challenges[name].content
        self.controls[-1] = self._active_content
        self.update()

    def on_nav_change(self, event):
        selected_challenge = list(self.challenges.values())[self.nav_bar.selected_index]
        self.page.go(f"/challenges/{selected_challenge.name}")

    def create_nav_bar(self) -> ft.NavigationBar:
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=challenge.icon, label=challenge.name)
                for challenge in self.challenges.values()
            ],
            selected_index=0,
            on_change=self.on_nav_change,
        )
