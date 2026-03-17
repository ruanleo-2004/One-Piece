from flask_ckeditor import CKEditor


def init_flask_ckeditor(app):
    ckeditor = CKEditor()
    ckeditor.init_app(app)
