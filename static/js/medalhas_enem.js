// === medalhasenem.js - Integração Exclusiva para Módulos ENEM ===
// Inclua <script src="/static/js/medalhasenem.js"></script> APENAS nos arquivos dos EXERCÍCIOS ENEM (musica, charge, tirinha, etc)!

(function() {
    // Atualiza os ícones de medalha ao lado de cada questão do exercício ENEM
    function atualizarMedalhasQuestoes(questoes) {
        const totalQuestoes = window.totalQuestoes || 5;
        for (let i = 1; i <= totalQuestoes; i++) {
            let el = document.querySelector(`[data-medalha-questao="${i}"]`);
            if (!el) {
                const btn = document.querySelector(`[data-questao="${i}"]`);
                if (btn) {
                    el = document.createElement('span');
                    el.setAttribute('data-medalha-questao', i);
                    el.style.marginLeft = '4px';
                    btn.parentNode.insertBefore(el, btn.nextSibling);
                }
            }
            if (el) {
                const tipo = questoes[i];
                if (tipo === "ouro") {
                    el.innerHTML = '<span title="Ouro" style="color:#fbc02d;font-size:1.25em;vertical-align:middle;"><i class="fa-solid fa-medal"></i></span> <span style="font-size:.95em;">Ouro</span>';
                } else if (tipo === "prata") {
                    el.innerHTML = '<span title="Prata" style="color:#90caf9;font-size:1.25em;vertical-align:middle;"><i class="fa-solid fa-medal"></i></span> <span style="font-size:.95em;">Prata</span>';
                } else if (tipo === "bronze") {
                    el.innerHTML = '<span title="Bronze" style="color:#bcaaa4;font-size:1.25em;vertical-align:middle;"><i class="fa-solid fa-medal"></i></span> <span style="font-size:.95em;">Bronze</span>';
                } else {
                    el.innerHTML = '';
                }
            }
        }
    }

    // Atualiza o quadro de medalhas do exercício ENEM atual
    function atualizarQuadroMedalhasEnem() {
        const nivelAtual = window.nivelAtual || 'ENEM_MUSICA';
        fetch('/minhas_medalhas_enem?nivel=' + encodeURIComponent(nivelAtual))
            .then(res => res.json())
            .then(data => {
                atualizarMedalhasQuestoes(data.questoes || {});
                if (window.parent && window.parent !== window) {
                    window.parent.postMessage({ medalhaGanha: true, modulo: nivelAtual }, "*");
                }
            });
    }

    // Função global para registrar medalha ENEM via backend, chamada pelo exercício
    window.premiarMedalhaEnem = function premiarMedalhaEnem(nivel, questao, medalha) {
        if (!nivel || !questao || !medalha) return;
        return fetch('/registrar_medalha_enem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nivel, questao, medalha})
        })
        .then(res => res.json())
        .then(data => {
            if (data && data.medalha) {
                setTimeout(atualizarQuadroMedalhasEnem, 120);
            }
        });
    };

    // Intercepta qualquer chamada AJAX/fetch para registrar medalha ENEM, atualizando o quadro de medalhas ao receber resposta
    function interceptaMedalhaEnem() {
        const oldFetch = window.fetch;
        window.fetch = function() {
            return oldFetch.apply(this, arguments).then(async resp => {
                if (arguments[0] && typeof arguments[0] === "string" && arguments[0].includes('/registrar_medalha_enem')) {
                    try {
                        const clone = resp.clone();
                        const json = await clone.json();
                        if (json && json.medalha) {
                            setTimeout(atualizarQuadroMedalhasEnem, 100);
                        }
                    } catch(e) {}
                }
                return resp;
            });
        };
        const open = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            this._isMedalhaEnem = url && url.includes('/registrar_medalha_enem');
            return open.apply(this, arguments);
        };
        const send = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            if (this._isMedalhaEnem) {
                this.addEventListener('readystatechange', function() {
                    if (this.readyState === 4 && this.status === 200) {
                        try {
                            const json = JSON.parse(this.responseText);
                            if (json && json.medalha) {
                                setTimeout(atualizarQuadroMedalhasEnem, 100);
                            }
                        } catch(e) {}
                    }
                });
            }
            return send.apply(this, arguments);
        };
    }

    document.addEventListener('DOMContentLoaded', function() {
        interceptaMedalhaEnem();
        setTimeout(atualizarQuadroMedalhasEnem, 300);
    });

    // Recebe mensagem do menu principal para atualizar o quadro de medalhas após premiação
    window.addEventListener("message", function(event) {
        if (event.data && event.data.medalhaGanha) {
            setTimeout(atualizarQuadroMedalhasEnem, 150);
        }
    });

})();