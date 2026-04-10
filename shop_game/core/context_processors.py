from shop_game.core.models import News, SiteSetting


def site_meta(request):
    """Expose site settings and latest published news to all templates."""
    site_setting = SiteSetting.objects.first()
    latest_news = News.objects.filter(is_published=True).order_by('-created_at')[:6]
    marquee_news = News.objects.filter(is_published=True).order_by('-created_at')[:10]
    return {
        'site_setting': site_setting,
        'latest_news': latest_news,
        'marquee_news': marquee_news,
    }
