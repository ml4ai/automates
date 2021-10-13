int main(){
    int x = 0;
    for(int i = 0; i < 10; i++){
        if((x + i) == 2){
            x++;
            continue;
        }
        if(x == 1){
            break;
        }
        if(x + i == 3){
            if (i % 2 == 0)
                continue;
            else
                break;
        }
        x = x + 1;
    }

}