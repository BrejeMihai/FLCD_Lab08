import sys
from Grammar import Grammar, Lr0Parser

if __name__ == '__main__':
    gr = Grammar()
    #gr.read_from_file(sys.argv[1])
    gr.read_from_file("C:\\Users\\Breje\\Desktop\\g1.txt")
    print(gr)
    #print(gr.get_productions_for_nonterminal("simpelStmt"))
    parser = Lr0Parser(gr)
    parser.canonical_collection()
    #parser.actual_parsing(['b','a','a','b'])

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
            word = input("Enter word >>> ")
            lista = word.split(" ")
            if len(lista) > 1:
                raise Exception("Single word accepted")
            proper_form_word = [x for x in word]
            parser.actual_parsing(proper_form_word)
        elif option == 0:
            break
        else:
            print("Invalid option!")
