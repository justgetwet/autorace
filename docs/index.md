---
layout: default
title: "Top Page"
---

<main>
  <section>
    {% for post in site.posts %}
      <aside>
        <h3>
          <div class="c-flex">
            <div class="date">{{ post.date | date: "%b %d, %y"}}</div>
            <div class="title">
              <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
            </div>
          </div>
        </h3>
      </aside>  
    {% endfor %}
  </section>
</main>
