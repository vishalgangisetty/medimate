public class PrimeNumberEasy {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter a number: ");
        int n = sc.nextInt();

        boolean isPrime = true;

        if (n <= 1) {
            isPrime = false;
        } else {
            // simple loop: 2 to n/2
            for (int i = 2; i <= n / 2; i++) {
                if (n % i == 0) {
                    isPrime = false;  // found a divisor
                    break;            // no need to check more
                }
            }
        }

        if (isPrime) {
            System.out.println(n + " is a Prime Number");
        } else {
            System.out.println(n + " is Not a Prime Number");
        }
    }
}