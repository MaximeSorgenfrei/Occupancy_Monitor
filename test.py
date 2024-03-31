from src import OccupancyMonitor

om = OccupancyMonitor(show_user_settings=True, diagnostics=True)
om.run(show_video_source=True)