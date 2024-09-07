def filter_files(files, file_type):
    """Фильтрует список файлов в зависимости от типа файла"""
    if file_type == 'documents':
        return [f for f in files if f.get('mime_type', '').startswith('application/')]
    elif file_type == 'images':
        return [f for f in files if f.get('mime_type', '').startswith('image/')]
    elif file_type == 'videos':
        return [f for f in files if f.get('mime_type', '').startswith('video/')]
    elif file_type == 'audio':
        return [f for f in files if f.get('mime_type', '').startswith('audio/')]
    elif file_type == 'archives':
        return [f for f in files if f.get('mime_type', '').startswith('application/zip') or 
                                    f.get('mime_type', '').startswith('application/x-rar-compressed')]
    elif file_type == 'others':
        return [f for f in files if not (f.get('mime_type', '').startswith('application/') or 
                                        f.get('mime_type', '').startswith('image/') or 
                                        f.get('mime_type', '').startswith('video/') or 
                                        f.get('mime_type', '').startswith('audio/'))]
    else:
        return files
