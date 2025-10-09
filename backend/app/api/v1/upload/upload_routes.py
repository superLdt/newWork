#!/usr/bin/env python3
"""
上传路由

提供图片与文档上传，并返回可访问的文件URL
"""

from flask import Blueprint
from .upload_controller import UploadController

upload_bp = Blueprint('upload', __name__)

# 图片上传
upload_bp.add_url_rule('/image', 'upload_image', UploadController.upload_image, methods=['POST'])

# 文档上传
upload_bp.add_url_rule('/document', 'upload_document', UploadController.upload_document, methods=['POST'])

# 通用附件上传
upload_bp.add_url_rule('/attachment', 'upload_attachment', UploadController.upload_attachment, methods=['POST'])

# 文件访问
upload_bp.add_url_rule('/files/<path:filepath>', 'serve_file', UploadController.serve_uploaded_file, methods=['GET'])