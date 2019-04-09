import unittest

from dataprep.split.beautify import beautify_text

text_boundaries = '''
<pad> <pad> <pad> public `w `C ar ti fact `C request `C builder w` `w ar ti fact w` ( final `C string `w group `C id w` , final `C string `w ar ti fact `C id w` , final `C string version , final `C string `w exten sion w` , final `C string `w class i fier w` ) { `w set `C ar ti fact w` ( new `w `C default `C ar ti fact w` ( `w group `C id w` , `w ar ti fact `C id w` , `w class i fier w` , `w exten sion w` , version ) ) ; return this ; } } ``
/* * `C copyright ( c ) `w 200 9 w` - `w 20 11 w` `w `C son at y pe w` , `C inc . * `C all `w right s w` `w re ser ved w` . `C this program and the `w ac comp any ing w` `w mat er i als w` * are `w ma de w` `w avai lable w` under the terms of the `C eclipse `C public `C license `w v 1 w` . 0 * and `C apache `C license `w v 2 w` . 0 which `w ac comp an i es w` this `w distribu tion w` . * `C the `C eclipse `C public `C license is `w avai lable w` at * http : // www . eclipse . org / legal / `w ep l w` - `w v 10 w` . html * `C the `C apache `C license `w v 2 w` . 0 is `w avai lable w` at * http : // www . apache . org / licenses / `Cs license - 2 . 0 . html * `C you may `w e le ct w` to `w re dist ribute w` this code under either of `w the se w` licenses . */ package org . `w son at y pe w` . `w s is u w` . `w m av en w` . `w b rid ge w` . `w sup port w` ; import java . util . `w `C array `C list w` ; import java . util . `C collection ; import org . apache . `w m av en w` . model . `w `C re pos it ory w` ; import org . `w son at y pe w` . `w a e ther w` . `w re pos it ory w` . `w `C remo te `C re pos it ory w` ; import org . `w son at y pe w` . `w a e ther w` . `w re pos it ory w` . `w `C re pos it ory `C po lic y w` ; /* * * `w `Cs to do w`
'''

text_boundaries_expected = '''
3x<pad> public ArtifactRequestBuilder artifact ( final String groupId , final String artifactId , final String version , final String extension , final String classifier ){
setArtifact ( new DefaultArtifact ( groupId , artifactId , classifier , extension , version ) );
return this;
}
}



/* * Copyright ( c ) 2009 - 2011 Sonatype , Inc.* All rights reserved.This program and the accompanying materials * are made available under the terms of the Eclipse Public License v1.0 * and Apache License v2.0 which accompanies this distribution.* The Eclipse Public License is available at * http : // www.eclipse.org / legal / epl - v10.html * The Apache License v2.0 is available at * http : // www.apache.org / licenses / LICENSE - 2.0.html * You may elect to redistribute this code under either of these licenses.*/
package org.sonatype.sisu.maven.bridge.support;
import java.util.ArrayList;
import java.util.Collection;
import org.apache.maven.model.Repository;
import org.sonatype.aether.repository.RemoteRepository;
import org.sonatype.aether.repository.RepositoryPolicy;
/* * * TODO
'''


# text_separators


class UtilTest(unittest.TestCase):
    def test_beautify_1(self):
        text_boundaries1 = '`w `C ar ti fact `C req uest `C build er `C cl ass w`'

        actual = beautify_text(text_boundaries1)

        expected = "ArtifactRequestBuilderClass"

        self.assertEqual(expected, actual)

    def test_beautify_2(self):
        text_boundaries1 = '`w `Cs to do w`'

        actual = beautify_text(text_boundaries1)

        expected = "TODO"

        self.assertEqual(expected, actual)

    def test_beautify_3(self):
        text_boundaries1 = '`w TO DO w`'

        actual = beautify_text(text_boundaries1)

        expected = "TODO"

        self.assertEqual(expected, actual)

    def test_beautify_boundaries(self):
        actual = beautify_text(text_boundaries)

        self.assertEqual(text_boundaries_expected, actual)


if __name__ == '__main__':
    unittest.main()
