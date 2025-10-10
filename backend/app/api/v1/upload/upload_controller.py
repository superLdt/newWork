#!/usr/bin/env python3
"""
上传控制器

处理文件上传相关的API请求
使用通用上传服务提供统一的上传功能
"""

import os
from flask import request, send_from_directory, current_app
from flask_jwt_extended import get_current_user
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from app.services.common.upload_service import UploadService
import logging

logger = logging.getLogger(__name__)


class UploadController:
    """
    上传控制器类，处理文件上传相关的API请求
    使用通用上传服务提供统一的上传功能
    """

    @staticmethod
    @permission_required('upload:image')
    def upload_image():
        """
        上传图片
        ---
        tags:
          - 文件上传
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: 图片文件
        responses:
          200:
            description: 上传成功
          400:
            description: 参数错误或文件类型不支持
          500:
            description: 服务器错误
        """
        try:
            file = request.files.get('file')
            if not file:
                return error_response('缺少文件参数', 400)

            # 获取当前用户
            current_user = get_current_user()
            user_id = current_user.id if current_user else None

            # 从请求中获取业务类型和业务ID
            business_type = request.form.get('business_type', 'general')
            business_id = request.form.get('business_id')

            # 使用通用上传服务
            success, result = UploadService.save_file(
                file=file,
                file_type='image',
                business_type=business_type,
                business_id=business_id,
                user_id=user_id
            )

            if success:
                return success_response(result, message='上传成功')
            else:
                return error_response(result.get('error', '上传失败'), 400)

        except Exception as e:
            logger.error(f"上传图片失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    @permission_required('upload:document')
    def upload_document():
        """
        上传文档
        ---
        tags:
          - 文件上传
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: 文档文件
        responses:
          200:
            description: 上传成功
          400:
            description: 参数错误或文件类型不支持
          500:
            description: 服务器错误
        """
        try:
            file = request.files.get('file')
            if not file:
                return error_response('缺少文件参数', 400)

            # 获取当前用户
            current_user = get_current_user()
            user_id = current_user.id if current_user else None

            # 从请求中获取业务类型和业务ID
            business_type = request.form.get('business_type', 'general')
            business_id = request.form.get('business_id')

            # 使用通用上传服务
            success, result = UploadService.save_file(
                file=file,
                file_type='document',
                business_type=business_type,
                business_id=business_id,
                user_id=user_id
            )

            if success:
                return success_response(result, message='上传成功')
            else:
                return error_response(result.get('error', '上传失败'), 400)

        except Exception as e:
            logger.error(f"上传文档失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    def upload_attachment(business_type: str = None, business_id: str = None):
        """
        通用附件上传接口
        支持指定业务类型和业务ID
        """
        try:
            file = request.files.get('file')
            if not file:
                return error_response('缺少文件参数', 400)

            # 获取业务参数
            business_type = business_type or request.form.get('business_type')
            business_id = business_id or request.form.get('business_id')

            # 获取当前用户
            current_user = get_current_user()
            user_id = current_user.id if current_user else None

            # 使用通用上传服务
            success, result = UploadService.save_file(
                file=file,
                file_type='attachment',
                business_type=business_type,
                business_id=business_id,
                user_id=user_id
            )

            if success:
                return success_response(result, message='上传成功')
            else:
                return error_response(result.get('error', '上传失败'), 400)

        except Exception as e:
            logger.error(f"上传附件失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    def serve_uploaded_file(filepath):
        """
        提供上传文件的静态访问
        ---
        tags:
          - 文件上传
        parameters:
          - name: filepath
            in: path
            type: string
            required: true
            description: 文件路径
        responses:
          200:
            description: 文件内容
          400:
            description: 非法路径
          404:
            description: 文件不存在
        """
        try:
            logger.info(f"[serve_uploaded_file] request received: filepath='{filepath}'")
            upload_root = current_app.config.get('UPLOAD_FOLDER')
            if not upload_root:
                upload_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'uploads')
                upload_root = os.path.abspath(upload_root)
            else:
                upload_root = os.path.abspath(upload_root)

            logger.debug(f"[serve_uploaded_file] resolved upload_root='{upload_root}'")

            directory = os.path.join(upload_root)
            # 保护：禁止路径穿越
            safe_path = os.path.normpath(os.path.join(directory, filepath))
            logger.debug(f"[serve_uploaded_file] computed safe_path='{safe_path}'")
            if not safe_path.startswith(os.path.abspath(directory)):
                logger.warning(f"[serve_uploaded_file] path traversal attempt: safe_path='{safe_path}', directory='{directory}'")
                return error_response('非法路径', 400)

            # 文件存在性检查
            if not os.path.exists(safe_path):
                logger.warning(f"[serve_uploaded_file] file not found: safe_path='{safe_path}', original filepath='{filepath}'")
                return error_response('文件不存在', 404)

            subdir, filename = os.path.split(safe_path)
            logger.info(f"[serve_uploaded_file] sending file: subdir='{subdir}', filename='{filename}'")
            return send_from_directory(subdir, filename, as_attachment=False)
        except Exception as e:
            logger.error(f"[serve_uploaded_file] error while serving file: {str(e)}", exc_info=True)
            return error_response(str(e), 500)