// === medalhas.js - Integração Automática e Modular para Exercícios ===
// Coloque este arquivo em /static/js/medalhas.js
// Inclua <script src="/static/js/medalhas.js"></script> APENAS nos arquivos dos EXERCÍCIOS (NUNCA no menu principal!)

(function() {
    // ---- Configurações: ajuste se mudar IDs ou número de questões ----
    const nivelAtual = (window.nivelAtual || 'A1'); // pode detectar via JS se preferir
    const totalQuestoes = window.totalQuestoes || 28; // defina window.totalQuestoes se variar

    // ---- Medalha por questão: injeta ícone ao lado das questões ----
    function atualizarMedalhasQuestoes(questoes) {
        for (let i = 1; i <= totalQuestoes; i++) {
            let el = document.querySelector(`[data-medalha-questao="${i}"]`);
            if (!el) {
                // Cria o span na primeira vez (não precisa mexer no HTML)
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
                    el.innerHTML = '<span title="Ouro" style="color:#fbc02d;font-size:1.2em;">🥇</span> <span style="font-size:.9em;">Ouro</span>';
                } else if (tipo === "prata") {
                    el.innerHTML = '<span title="Prata" style="color:#b0bec5;font-size:1.2em;">🥈</span> <span style="font-size:.9em;">Prata</span>';
                } else if (tipo === "bronze") {
                    el.innerHTML = '<span title="Bronze" style="color:#cd7f32;font-size:1.2em;">🥉</span> <span style="font-size:.9em;">Bronze</span>';
                } else {
                    el.innerHTML = '';
                }
            }
        }
    }

    // ---- Atualiza as medalhas das questões e avisa o menu principal para atualizar o placar do topo ----
    function atualizarQuadroMedalhas() {
        fetch('/minhas_medalhas')
            .then(res => res.json())
            .then(data => {
                atualizarMedalhasQuestoes(data.questoes || {});
                // Avise o menu principal (pai) para atualizar o placar global do topo
                if (window.parent && window.parent !== window) {
                    window.parent.postMessage({ medalhaGanha: true }, "*");
                }
            });
    }

    // ---- Função global para registrar medalha (chame sempre ao ganhar medalha em questão) ----
    // Uso: premiarMedalha('A1', 3, 'ouro');
    window.premiarMedalha = function premiarMedalha(nivel, questao, medalha) {
        // Só registra se params válidos
        if (!nivel || !questao || !medalha) return;
        return fetch('/registrar_medalha', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nivel, questao, medalha})
        })
        .then(res => res.json())
        .then(data => {
            if (data && data.medalha) {
                setTimeout(atualizarQuadroMedalhas, 120);
            }
        });
    };

    // ---- Intercepta fetch/AJAX globalmente para atualizar sempre que ganhar medalha ----
    function interceptaMedalha() {
        // Intercepta fetch API
        const oldFetch = window.fetch;
        window.fetch = function() {
            return oldFetch.apply(this, arguments).then(async resp => {
                // Só intercepta chamadas para /registrar_medalha
                if (arguments[0] && typeof arguments[0] === "string" && arguments[0].includes('/registrar_medalha')) {
                    try {
                        const clone = resp.clone();
                        const json = await clone.json();
                        if (json && json.medalha) {
                            setTimeout(atualizarQuadroMedalhas, 100); // Atualiza medalhas locais e avisa o pai
                        }
                    } catch(e) {}
                }
                return resp;
            });
        };
        // Intercepta XMLHttpRequest (AJAX antigo)
        const open = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            this._isMedalha = url && url.includes('/registrar_medalha');
            return open.apply(this, arguments);
        };
        const send = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            if (this._isMedalha) {
                this.addEventListener('readystatechange', function() {
                    if (this.readyState === 4 && this.status === 200) {
                        try {
                            const json = JSON.parse(this.responseText);
                            if (json && json.medalha) {
                                setTimeout(atualizarQuadroMedalhas, 100);
                            }
                        } catch(e) {}
                    }
                });
            }
            return send.apply(this, arguments);
        };
    }

    // ---- NÃO cria placar do topo no exercício! ----
    // O placar global é responsabilidade do menu principal
    // Este script só cuida dos ícones ao lado das questões e avisa o menu principal para atualizar o topo

    // ---- Ao carregar a página do exercício ----
    document.addEventListener('DOMContentLoaded', function() {
        interceptaMedalha();
        setTimeout(atualizarQuadroMedalhas, 300); // Aguarda HTML carregar
    });

    // Atualize sempre que voltar do menu, para garantir atualização visual das medalhas
    window.addEventListener("message", function(event) {
        if (event.data && event.data.medalhaGanha) {
            setTimeout(atualizarQuadroMedalhas, 150);
        }
    });

})();