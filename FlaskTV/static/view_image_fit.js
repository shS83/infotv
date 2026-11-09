/*
 * Fit Kothing editor images into the visible InfoTV screen.
 *
 * Some TV Opera/Presto browsers do not support the flexbox layout in
 * view_base.css. In those browsers max-height: 100% is not enough because
 * the figure has no reliably computed height. Use actual pixel dimensions
 * as a fallback, without changing the saved info_pages/*.html files.
 *
 * Deliberately written in old-style JavaScript (no ES6, observers or libs).
 */
(function (window, document) {
    'use strict';

    var supportsFlex = (function () {
        var probe = document.createElement('div');
        probe.style.display = 'flex';
        return probe.style.display === 'flex';
    }());

    function viewportWidth() {
        return document.documentElement.clientWidth ||
            window.innerWidth || document.body.clientWidth || 1920;
    }

    function viewportHeight() {
        return document.documentElement.clientHeight ||
            window.innerHeight || document.body.clientHeight || 1080;
    }

    function isImageContainer(element) {
        return element && element.nodeType === 1 &&
            (' ' + element.className + ' ').indexOf(' ke-image-container ') !== -1;
    }

    function imageContainer(image, page) {
        var node = image.parentNode;
        while (node && node !== page) {
            if (isImageContainer(node)) return node;
            node = node.parentNode;
        }
        return null;
    }

    function originalDimensions(image) {
        var width = image.naturalWidth || 0;
        var height = image.naturalHeight || 0;

        /* A number of editor-saved images also carry their source dimensions. */
        if (!width || !height) {
            var origin = image.getAttribute('origin-size') || '';
            var match = /^(\d+)\s*,\s*(\d+)$/.exec(origin);
            if (match) {
                width = parseInt(match[1], 10);
                height = parseInt(match[2], 10);
            }
        }

        /* Older browsers may not expose naturalWidth/naturalHeight. */
        if (!width || !height) {
            width = image._infotvSourceWidth || image.width;
            height = image._infotvSourceHeight || image.height;
        }
        if (width > 0 && height > 0) {
            image._infotvSourceWidth = width;
            image._infotvSourceHeight = height;
        }
        return {width: width, height: height};
    }

    function setImportant(style, name, value) {
        if (style.setProperty) {
            style.setProperty(name, value, 'important');
        } else {
            /* Old CSSOM implementations: keep the override at inline priority. */
            style.cssText += '; ' + name + ': ' + value + ' !important;';
        }
    }

    function fitImages() {
        var divs = document.getElementsByTagName('div');
        var screenW = viewportWidth();
        var screenH = viewportHeight();
        var i, j, page, images, image, container, figure, dimensions;
        var top, pageTop, width, height, scale, displayW, displayH;

        for (i = 0; i < divs.length; i++) {
            page = divs[i];
            if ((' ' + page.className + ' ').indexOf(' info-page ') === -1) {
                continue;
            }

            images = page.getElementsByTagName('img');
            for (j = 0; j < images.length; j++) {
                image = images[j];
                container = imageContainer(image, page);
                if (!container) continue;

                /* Text above the image must keep its space on the slide. */
                pageTop = page.getBoundingClientRect().top;
                top = container.getBoundingClientRect().top;
                width = Math.max(1, Math.min(screenW, page.clientWidth || screenW));
                height = Math.max(1, screenH - Math.max(0, top - pageTop));
                height = Math.min(height, screenH);

                dimensions = originalDimensions(image);
                setImportant(image.style, 'max-width', width + 'px');
                setImportant(image.style, 'max-height', height + 'px');

                if (dimensions.width > 0 && dimensions.height > 0) {
                    scale = Math.min(1, width / dimensions.width,
                        height / dimensions.height);
                    displayW = Math.max(1, Math.floor(dimensions.width * scale));
                    displayH = Math.max(1, Math.floor(dimensions.height * scale));
                    setImportant(image.style, 'width', displayW + 'px');
                    setImportant(image.style, 'height', displayH + 'px');
                } else {
                    /* The image has not decoded yet; onload will size it. */
                    setImportant(image.style, 'width', 'auto');
                    setImportant(image.style, 'height', 'auto');
                    displayH = 0;
                }

                /* Presto without flexbox: center the fitted picture in its box. */
                if (!supportsFlex) {
                    figure = image.parentNode;
                    container.style.height = height + 'px';
                    if (figure && figure.tagName.toLowerCase() === 'figure') {
                        figure.style.height = height + 'px';
                    }
                    image.style.marginTop = Math.max(0,
                        Math.floor((height - displayH) / 2)) + 'px';
                }

                if (!image.complete && !image._infotvFitOnLoad) {
                    image._infotvFitOnLoad = true;
                    if (image.addEventListener) {
                        image.addEventListener('load', fitImages, false);
                    } else if (image.attachEvent) {
                        image.attachEvent('onload', fitImages);
                    }
                }
            }
        }
    }

    window.InfoTVFitImages = fitImages;

    if (document.readyState === 'loading' && document.addEventListener) {
        document.addEventListener('DOMContentLoaded', fitImages, false);
    } else {
        fitImages();
    }

    if (window.addEventListener) {
        window.addEventListener('resize', fitImages, false);
        window.addEventListener('load', fitImages, false);
    } else if (window.attachEvent) {
        window.attachEvent('onresize', fitImages);
        window.attachEvent('onload', fitImages);
    }
}(window, document));
