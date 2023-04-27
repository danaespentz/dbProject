@app.route('/<user_name>/search_results', methods=['GET', 'POST'])
def search_results():
    title = request.form.get("title")
    author = request.form.get("author")
    theme_categories = request.form.get("theme_categories")

    if not title and not author and not theme_categories:
        return render_template('search_results.html', error_message="All fields are empty !")

    # Perform search on fake books database
    results=list()
    for book in books:
        if title==book['title']:
            results.append(book)
        if author:
            if author==book['author']:
                results.append(book)
        if theme_categories:
            if theme_categories==book['theme_categories']:
                results.append(book)
    
    if not results:
        return render_template('search_results.html', error_message="Not found.. Sorry :(")
        
    return render_template('search_results.html', results=results)
