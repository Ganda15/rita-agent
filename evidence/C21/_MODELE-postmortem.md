# INC-NNN — <le symptôme observé, pas la cause supposée>

> **Gabarit.** Copier ce fichier, le renommer `INC-NNN-<mot-cle>.md`, et le remplir.
> Les six sections correspondent aux **5 critères officiels de C21** (voir `README.md`) —
> aucune n'est décorative : en sauter une, c'est perdre le critère qu'elle porte.
>
> ⚠️ **Le titre décrit ce qu'on a VU, pas ce qu'on a compris.** Au moment de la détection, la
> cause est inconnue. Titrer par la cause fait croire à une évidence rétrospective, et masque
> justement le travail de diagnostic que le critère 1 demande de montrer.

| | |
|---|---|
| **Détecté le** | <date, et **comment** : test rouge, alerte, remontée d'usage, lecture de code> |
| **Sévérité** | <P1 service inutilisable · P2 fonction dégradée · P3 gêne> |
| **Durée** | <de la détection à la correction vérifiée> |
| **Impact réel** | <ce qui a été perdu ou faussé — et si rien, l'écrire> |
| **Commit du correctif** | `<sha>` |
| **Issue / demande de fusion** | <numéro, ou **« aucune — commit direct »** si c'est le cas> |

## 1. Ce qu'on a vu *(critère 1 — le symptôme, avant la cause)*

<Message d'erreur exact, sortie de commande, capture. Verbatim, pas reformulé.>

## 2. Cause racine *(critère 1)*

<La vraie origine. Distinguer la cause **technique** de la cause **de conception** : pourquoi
le défaut a-t-il pu exister ET passer inaperçu ? Le second point est celui qui a de la valeur.>

## 3. Reproduction en développement *(critère 2)*

<La commande exacte qui reproduit le défaut, et sa sortie. Si le défaut ne se reproduit pas,
l'écrire — c'est une information, pas un échec.>

```
<commande>
<sortie observée>
```

## 4. Procédure de débogage *(critère 3)*

<Le déroulé réel, étape par étape, **y compris les fausses pistes**. Un débogage qui va droit
au but ne s'est pas produit ainsi : on a écarté des hypothèses, et les écarter est du travail.>

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | | | |

## 5. Correction, étape par étape *(critère 4)*

<Chaque étape. Pas « corrigé le fichier X » mais ce qui a été changé et **pourquoi ce
choix-là** plutôt qu'un autre.>

## 6. Vérification et non-régression *(critères 2 et 5)*

<Comment on sait que c'est corrigé — la sortie, pas l'intention. Puis le **test** qui échouerait
si le défaut revenait.>

```
<vérification et son résultat>
```

**Test de non-régression** : `tests/<fichier>::<test>`

## 7. Ce que ça change pour la suite

<La contre-mesure. Si aucune n'est prise, l'écrire et dire pourquoi — un incident sans suite
assumée vaut mieux qu'une bonne intention non tenue.>
