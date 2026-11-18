import org.apache.spark.util.DependencyUtils;
import scala.Option;

public final class ResolveSparkPackages {
    public static void main(String[] args) {
        var jars = DependencyUtils.resolveMavenDependencies(
            true, args[1], args[0], null, null, Option.apply(args[2])
        ).iterator();
        while (jars.hasNext()) {
            System.out.println("jar=" + jars.next());
        }
    }
}
