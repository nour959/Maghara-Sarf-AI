import os
import re

class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 1
        # Point 1.1 & 5 : Liste des dérivés validés et leur fréquence
        self.derived_words = {} 

class SARF_Logic:
    def __init__(self):
        self.root_tree = None
        self.schemes = {} # Point 1.2 : Table de hachage

    def is_arabic_triple(self, text):
        # Sécurité : 3 lettres arabes uniquement, pas de français
        return bool(re.match(r'^[\u0621-\u064A]{3}$', text))

    # --- Gestion AVL (Complexité Logarithmique) ---
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def insert_root(self, root, key):
        if not root: return Node(key)
        if key < root.key: root.left = self.insert_root(root.left, key)
        elif key > root.key: root.right = self.insert_root(root.right, key)
        else: return root # Déjà existant

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        # Note: Les rotations d'équilibrage peuvent être ajoutées ici pour un AVL strict
        return root

    def search_root(self, root, key):
        if not root or root.key == key: return root
        if key < root.key: return self.search_root(root.left, key)
        return self.search_root(root.right, key)

    def delete_root(self, root, key):
        if not root: return root
        if key < root.key: root.left = self.delete_root(root.left, key)
        elif key > root.key: root.right = self.delete_root(root.right, key)
        else:
            if not root.left: return root.right
            if not root.right: return root.left
            temp = self._min_node(root.right)
            root.key = temp.key
            root.right = self.delete_root(root.right, temp.key)
        return root

    def _min_node(self, node):
        curr = node
        while curr.left: curr = curr.left
        return curr

    # --- Moteur de Dérivation (Point 2.1) ---
    def apply_scheme(self, root_word, scheme_name):
        if len(root_word) != 3: return None
        res = ""
        for char in scheme_name:
            if char == 'ف': res += root_word[0]
            elif char == 'ع': res += root_word[1]
            elif char == 'ل': res += root_word[2]
            else: res += char
        return res

    # --- Vérification et Mise à jour (Point 2.2 & 5) ---
    def verify_morphology(self, word, root_key):
        node = self.search_root(self.root_tree, root_key)
        if not node: return False, None
        
        for s_name in self.schemes:
            if self.apply_scheme(root_key, s_name) == word:
                # Mise à jour automatique de la liste des dérivés validés
                node.derived_words[word] = node.derived_words.get(word, 0) + 1
                return True, s_name
        return False, None

    # --- Identification de la racine ---
    def identify_word(self, word):
        results = []
        w_clean = word.replace('َ','').replace('ُ','').replace('ِ','').replace('ْ','')
        for s_name in self.schemes:
            s_clean = s_name.replace('َ','').replace('ُ','').replace('ِ','').replace('ْ','')
            if len(w_clean) == len(s_clean):
                r1, r2, r3, possible = None, None, None, True
                for wc, sc in zip(w_clean, s_clean):
                    if sc == 'ف': r1 = wc
                    elif sc == 'ع': r2 = wc
                    elif sc == 'ل': r3 = wc
                    elif wc != sc: possible = False; break
                if possible and r1 and r2 and r3:
                    root_cand = r1 + r2 + r3
                    if self.search_root(self.root_tree, root_cand):
                        results.append({"root": root_cand, "scheme": s_name, "word": word})
        return results

    def get_all_roots_data(self, node, res):
        if node:
            self.get_all_roots_data(node.left, res)
            res.append({"root": node.key, "derivatives": node.derived_words})
            self.get_all_roots_data(node.right, res)
        return res

    def load_data(self, r_path, s_path):
        if os.path.exists(r_path):
            with open(r_path, 'r', encoding='utf-8') as f:
                for line in f:
                    r = line.strip()
                    if self.is_arabic_triple(r): self.root_tree = self.insert_root(self.root_tree, r)
        if os.path.exists(s_path):
            with open(s_path, 'r', encoding='utf-8') as f:
                for line in f:
                    p = line.strip().split(',')
                    if len(p) >= 1: self.schemes[p[0]] = {"cat": p[1] if len(p)>1 else ""}