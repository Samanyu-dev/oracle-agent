import os

from hf_space.app import build_ui

if __name__ == '__main__':
    app = build_ui()
    port = int(os.environ.get('PORT', 7860))
    app.launch(server_name='0.0.0.0', server_port=port)
