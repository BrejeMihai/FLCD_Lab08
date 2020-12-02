import sys
from Grammar import Grammar, Lr0Parser

if __name__ == '__main__':
    gr = Grammar()
    gr.read_from_file(sys.argv[1])
    print(gr)
    parser = Lr0Parser(gr)
    parser.canonical_collection()

    _menu_string = "Choose an option:\n1.Show the grammar details.\n2.Show productions for nonterminal.\n3.Show parsing table.\n4.Parse word\n0.Exit"
    end = False
    while(end != True):
        print(_menu_string)
        option = int(input(">>> "))

        if option == 1:
            print(gr)
        elif option == 2:
            non_terminal = input()
            print(gr.get_productions_for_nonterminal(non_terminal))
        elif option == 3:
            parser.show_parsing_table()
        elif option == 4:
            word = input("Enter sequence >>> ")
            lista = word.split(" ")
            if len(lista) > 1:
                raise Exception("Sequence not accepted")
            proper_form_word = [x for x in word]
            parser.actual_parsing(proper_form_word)
        elif option == 0:
            break
        else:
            print("Invalid option!")
