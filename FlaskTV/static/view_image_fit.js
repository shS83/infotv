/*
 * Auto-size InfoTV images for TV Opera/Presto and ordinary browsers.
 * Each slide keeps its original image aspect ratio. No editor pages are changed.
 * ES5-era syntax deliberately used for old embedded TV browsers.
 *
 * Optional TV diagnostics: /view?debug=true (also works with &debug=true)
 * Optional test on a modern browser: /view?legacyfit=1
 */
(function (window, document) {
    'use strict';

    var ua = (window.navigator && window.navigator.userAgent) || '';
    var query = (window.location && window.location.search) || '';
    var supports = document.createElement('div');
    supports.style.display = 'flex';
    supports.style.height = '100vh';

    /* Opera 12.1 supports flexbox but not vh; TV forks vary widely. */
    var legacy = /Presto|Opera TV|Opera\/[0-9]/i.test(ua) ||
        supports.style.display !== 'flex' ||
        supports.style.height !== '100vh' ||
        /(?:\?|&)legacyfit=1(?:&|$)/.test(query);
    var debug = /(?:\?|&)debug=(?:true|1)(?:&|$)/i.test(query) ||
        /(?:\?|&)fitdebug=1(?:&|$)/.test(query);
    var root = document.documentElement;
    var debugBox = null;
    var running = false;

    if (legacy && (' ' + root.className + ' ').indexOf(' infotv-legacy ') === -1) {
        root.className += ' infotv-legacy';
    }

    function screenSize() {
        var html = document.documentElement;
        var body = document.body;
        return {
            width: html.clientWidth || window.innerWidth || (body && body.clientWidth) || 1920,
            height: html.clientHeight || window.innerHeight || (body && body.clientHeight) || 1080
        };
    }

    function hasClass(element, className) {
        return element && element.nodeType === 1 &&
            (' ' + element.className + ' ').indexOf(' ' + className + ' ') !== -1;
    }

    function findContainer(image, page) {
        var node = image.parentNode;
        while (node && node !== page) {
            if (hasClass(node, 'ke-image-container')) return node;
            node = node.parentNode;
        }
        return null;
    }

    function realSize(image) {
        var w = image.naturalWidth || image._infotvNaturalWidth || 0;
        var h = image.naturalHeight || image._infotvNaturalHeight || 0;
        var match;
        var origin = image.getAttribute('origin-size') || '';

        if (!w || !h) {
            match = /^(\d+)\s*,\s*(\d+)$/.exec(origin);
            if (match) {
                w = parseInt(match[1], 10);
                h = parseInt(match[2], 10);
            }
        }

        /* An unstyled Image() gives true dimensions even on older browsers
           that lack naturalWidth / naturalHeight on the displayed <img>. */
        if ((!w || !h) && !image._infotvProbe) {
            image._infotvProbe = new Image();
            image._infotvProbe.onload = function () {
                image._infotvNaturalWidth = this.naturalWidth || this.width;
                image._infotvNaturalHeight = this.naturalHeight || this.height;
                fitImages();
            };
            image._infotvProbe.src = image.src;
            if (image._infotvProbe.complete) {
                w = image._infotvProbe.naturalWidth || image._infotvProbe.width;
                h = image._infotvProbe.naturalHeight || image._infotvProbe.height;
            }
        }
        return {width: w || 0, height: h || 0};
    }

    function contentTop(page, container) {
        var top = 0;
        var pageRect = page.getBoundingClientRect();
        var child = page.firstChild;
        var rect;
        while (child && child !== container) {
            if (child.nodeType === 1 && child.tagName.toLowerCase() !== 'style') {
                rect = child.getBoundingClientRect();
                if (rect.bottom - pageRect.top > top) top = rect.bottom - pageRect.top;
            }
            child = child.nextSibling;
        }
        return Math.max(0, Math.ceil(top));
    }

    function showDebug(message) {
        if (!debug || !document.body) return;
        if (!debugBox) {
            debugBox = document.createElement('div');
            debugBox.id = 'infotv-fit-debug';
            /* Fixed pixel position works with old Opera; no flexbox needed. */
            debugBox.style.cssText = 'position:fixed;left:6px;top:6px;' +
                'z-index:2147483647;background:#000;color:#fff;' +
                'font:14px/1.35 monospace;white-space:pre;' +
                'padding:8px;border:2px solid #00ff99;opacity:0.95;' +
                'max-width:95%;overflow:hidden;';
            document.body.appendChild(debugBox);
        }
        /* Use textContent where available, no innerHTML needed. */
        if ('textContent' in debugBox) debugBox.textContent = message;
        else debugBox.innerText = message;
    }

    function fitImages() {
        if (running || !document.body) return;
        running = true;
        try {
            var size = screenSize();
            var pages = document.getElementsByTagName('div');
            var i, j, page, imgs, img, container, figure;
            var y, availWidth, availHeight, measured, factor, imgW, imgH;
            var screen = window.screen || {};
            var html = document.documentElement;
            var body = document.body;
            var pageCount = 0, imageCount = 0;
            var diag = 'InfoTV DIAGNOSTIIKKA (?debug=true)' +
                '\nSelain: ' + ua.substring(0, 120) +
                '\nViewport: ' + size.width + ' x ' + size.height +
                '\ninnerWidth/Height: ' + (window.innerWidth || '?') +
                ' x ' + (window.innerHeight || '?') +
                '\nScreen: ' + (screen.width || '?') + ' x ' + (screen.height || '?') +
                ' | avail: ' + (screen.availWidth || '?') + ' x ' + (screen.availHeight || '?') +
                '\nDPR: ' + (window.devicePixelRatio || '?') +
                ' | mode: ' + (document.compatMode || '?') +
                ' | legacy: ' + (legacy ? 'YES' : 'NO') +
                '\nHTML client: ' + html.clientWidth + 'x' + html.clientHeight +
                ' scroll: ' + html.scrollWidth + 'x' + html.scrollHeight +
                '\nBODY client: ' + body.clientWidth + 'x' + body.clientHeight +
                ' scroll: ' + body.scrollWidth + 'x' + body.scrollHeight;

            for (i = 0; i < pages.length; i++) {
                page = pages[i];
                if (!hasClass(page, 'info-page')) continue;
                pageCount++;

                if (legacy) {
                    /* Eliminate broken 100vh and flex height in TV Opera. */
                    page.style.width = size.width + 'px';
                    page.style.height = size.height + 'px';
                }

                if (debug) {
                    var pr = page.getBoundingClientRect();
                    diag += '\nPAGE rect: ' + Math.round(pr.left) + ',' +
                        Math.round(pr.top) + ' ' + Math.round(pr.right - pr.left) +
                        'x' + Math.round(pr.bottom - pr.top);
                }

                imgs = page.getElementsByTagName('img');
                for (j = 0; j < imgs.length; j++) {
                    img = imgs[j];
                    container = findContainer(img, page);
                    if (!container) continue;
                    imageCount++;
                    figure = img.parentNode;

                    if (legacy) {
                        y = contentTop(page, container);
                    } else {
                        y = Math.max(0, Math.ceil(
                            container.getBoundingClientRect().top - page.getBoundingClientRect().top));
                    }

                    availWidth = Math.max(1, Math.min(size.width, page.clientWidth || size.width));
                    availHeight = Math.max(1, size.height - y);
                    measured = realSize(img);

                    if (legacy) {
                        container.style.cssText = 'position:absolute !important;display:block !important;' +
                            'left:0 !important;top:' + y + 'px !important;' +
                            'width:' + availWidth + 'px !important;height:' + availHeight + 'px !important;' +
                            'min-width:0 !important;max-width:none !important;' +
                            'min-height:0 !important;max-height:none !important;' +
                            'float:none !important;overflow:hidden !important;' +
                            'padding:0 !important;margin:0 !important;text-align:center !important;';
                        if (figure && figure.tagName.toLowerCase() === 'figure') {
                            figure.style.cssText = 'display:block !important;' +
                                'width:' + availWidth + 'px !important;' +
                                'height:' + availHeight + 'px !important;' +
                                'margin:0 !important;overflow:hidden !important;';
                        }
                    }

                    if (measured.width && measured.height) {
                        factor = Math.min(1, availWidth / measured.width,
                            availHeight / measured.height);
                        imgW = Math.max(1, Math.floor(measured.width * factor));
                        imgH = Math.max(1, Math.floor(measured.height * factor));
                        /* Rewrite the editor's inline height:1080px in old Opera.
                           CSS important alone isn't reliable in all TV forks. */
                        img.style.cssText = 'display:block !important;' +
                            'width:' + imgW + 'px !important;' +
                            'height:' + imgH + 'px !important;' +
                            'max-width:none !important;max-height:none !important;' +
                            'min-width:0 !important;min-height:0 !important;' +
                            'margin:0 auto !important;';
                        img.width = imgW;
                        img.height = imgH;
                        if (legacy) {
                            img.style.marginTop = Math.max(0,
                                Math.floor((availHeight - imgH) / 2)) + 'px';
                        }
                    } else {
                        /* Until image decoding finishes, keep it inside the box. */
                        img.style.cssText = 'display:block !important;' +
                            'max-width:' + availWidth + 'px !important;' +
                            'max-height:' + availHeight + 'px !important;' +
                            'margin:0 auto !important;';
                        imgW = 0;
                        imgH = 0;
                    }
                    if (debug && imageCount <= 3) {
                        var ir = img.getBoundingClientRect();
                        var cr = container.getBoundingClientRect();
                        diag += '\nIMG #' + imageCount + ' natural: ' +
                            measured.width + 'x' + measured.height +
                            ' | set: ' + imgW + 'x' + imgH +
                            '\n  visible: ' + Math.round(ir.right - ir.left) +
                            'x' + Math.round(ir.bottom - ir.top) +
                            ' @ ' + Math.round(ir.left) + ',' + Math.round(ir.top) +
                            '\n  container: ' + Math.round(cr.right - cr.left) +
                            'x' + Math.round(cr.bottom - cr.top) +
                            ' | available: ' + availWidth + 'x' + availHeight;
                    }
                }
            }
            if (debug) {
                diag += '\nSivuja: ' + pageCount + ' | kuvia: ' + imageCount;
                if (screen.width && size.width && screen.width / size.width >= 1.6) {
                    diag += '\nHUOM: screen/viewport-leveyssuhde ' +
                        (Math.round(screen.width / size.width * 100) / 100) +
                        'x (selainzoom / TV-skaalaus?)';
                }
            }
            showDebug(diag);
        } catch (error) {
            showDebug('InfoTV debug: kuvansovitusvirhe\n' +
                (error && error.message ? error.message : error));
        } finally {
            running = false;
        }
    }

    window.InfoTVFitImages = fitImages;
    if (document.readyState === 'loading' && document.addEventListener) {
        document.addEventListener('DOMContentLoaded', fitImages, false);
    } else {
        fitImages();
    }
    if (window.addEventListener) {
        window.addEventListener('load', fitImages, false);
        window.addEventListener('resize', fitImages, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', fitImages);
        window.attachEvent('onresize', fitImages);
    }
}(window, document));
