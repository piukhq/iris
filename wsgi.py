def init_app():
    from iris import app
    from prometheus import start_metrics

    start_metrics()
    return app


app = init_app()

if __name__ == "__main__":
    app.run()
