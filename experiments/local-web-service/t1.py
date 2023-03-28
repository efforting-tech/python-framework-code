



#s = service('0.0.0.0', 8080)
#script_renderer = contents_processor()



html_renderer = contents_processor(cache_files=True)

#s.register_path('/scripts', serve_directory_contents('/data/scripts', contents_processor=script_renderer))
#s.start()



print(html_renderer.render_file('data/html/index.html'))