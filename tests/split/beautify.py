import unittest

from dataprep.parse.model.placeholders import placeholders
from dataprep.split.beautify import beautify_text

ws = placeholders['word_start']
we = placeholders['word_end']
cap = placeholders['capital']
caps = placeholders['capitals']
ect = placeholders['ect']

text_boundaries = f'''
public {ws} {cap} ar ti fact {cap} request {cap} builder {we} {ws} ar ti fact {we} ( final {cap} string {ws} group {cap} id {we} , final {cap} string {ws} ar ti fact {cap} id {we} , final {cap} string version , final {cap} string {ws} exten sion {we} , final {cap} string {ws} class i fier {we} ) {{ {ws} set {cap} ar ti fact {we} ( new {ws} {cap} default {cap} ar ti fact {we} ( {ws} group {cap} id {we} , {ws} ar ti fact {cap} id {we} , {ws} class i fier {we} , {ws} exten sion {we} , version ) ) ; return this ; }} }} {ect}
/* * {cap} copyright ( c ) {ws} 200 9 {we} - {ws} 20 11 {we} {ws} {cap} son at y pe {we} , {cap} inc . * {cap} all {ws} right s {we} {ws} re ser ved {we} . {cap} this program and the {ws} ac comp any ing {we} {ws} mat er i als {we} * are {ws} ma de {we} {ws} avai lable {we} under the terms of the {cap} eclipse {cap} public {cap} license {ws} v 1 {we} . 0 * and {cap} apache {cap} license {ws} v 2 {we} . 0 which {ws} ac comp an i es {we} this {ws} distribu tion {we} . * {cap} the {cap} eclipse {cap} public {cap} license is {ws} avai lable {we} at * http : // www . eclipse . org / legal / {ws} ep l {we} - {ws} v 10 {we} . html * {cap} the {cap} apache {cap} license {ws} v 2 {we} . 0 is {ws} avai lable {we} at * http : // www . apache . org / licenses / {caps} license - 2 . 0 . html * {cap} you may {ws} e le ct {we} to {ws} re dist ribute {we} this code under either of {ws} the se {we} licenses . */ package org . {ws} son at y pe {we} . {ws} s is u {we} . {ws} m av en {we} . {ws} b rid ge {we} . {ws} sup port {we} ; import java . util . {ws} {cap} array {cap} list {we} ; import java . util . {cap} collection ; import org . apache . {ws} m av en {we} . model . {ws} {cap} re pos it ory {we} ; import org . {ws} son at y pe {we} . {ws} a e ther {we} . {ws} re pos it ory {we} . {ws} {cap} remo te {cap} re pos it ory {we} ; import org . {ws} son at y pe {we} . {ws} a e ther {we} . {ws} re pos it ory {we} . {ws} {cap} re pos it ory {cap} po lic y {we} ; /* * * {ws} {caps} to do {we}
'''

text_boundaries_expected = '''
public ArtifactRequestBuilder artifact ( final String groupId , final String artifactId , final String version , final String extension , final String classifier ){
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
        text_boundaries1 = f'{ws} {cap} ar ti fact {cap} req uest {cap} build er {cap} cl ass {we}'

        actual = beautify_text(text_boundaries1)

        expected = "ArtifactRequestBuilderClass"

        self.assertEqual(expected, actual)

    def test_beautify_2(self):
        text_boundaries1 = f'{ws} {caps} to do {we}'

        actual = beautify_text(text_boundaries1)

        expected = "TODO"

        self.assertEqual(expected, actual)

    def test_beautify_3(self):
        text_boundaries1 = f'{ws} TO DO {we}'

        actual = beautify_text(text_boundaries1)

        expected = "TODO"

        self.assertEqual(expected, actual)

    def test_beautify_boundaries(self):
        actual = beautify_text(text_boundaries)

        self.assertEqual(text_boundaries_expected, actual)


if __name__ == '__main__':
    unittest.main()
